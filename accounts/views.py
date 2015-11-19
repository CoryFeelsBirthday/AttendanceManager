from django.shortcuts import render, get_object_or_404, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from records.models import Zone, Program, Schedule
from django.db.models import Q
from .forms import AddUserForm, UserPermForm
from .models import get_user_profile, UserProfile
import json
from django.core.context_processors import csrf
from crispy_forms.utils import render_crispy_form
from django.contrib.auth.models import User


@require_http_methods(["GET", "POST"])
@login_required
def profile_view(request):
    profile = get_user_profile(request.user)
    if request.method == "GET":
        profile_form = ProfileForm(initial={'first_name': request.user.first_name,
                                            'last_name': request.user.last_name,
                                            'address': profile.address,
                                            'phone_number': profile.phone_number,
                                            'email': request.user.email})

        return render(request, "accounts_profile.html", {'profile_form': profile_form})
    else:
        profile_form = ProfileForm(request.POST)
        if profile_form.is_valid():
            # since this form is not a form for model we assign its values to both user and user profile
            setattr(request.user, 'first_name', profile_form.cleaned_data['first_name'])
            setattr(request.user, 'last_name', profile_form.cleaned_data['last_name'])
            setattr(profile, 'address', profile_form.cleaned_data['address'])
            setattr(profile, 'phone_number', profile_form.cleaned_data['phone_number'])
            setattr(request.user, 'email', profile_form.cleaned_data['email'])
            return render(request, "accounts_profile.html", {'profile_form': profile_form, 'success': True})
        else:
            return render(request, "accounts_profile.html", {'profile_form': profile_form})


def get_user_permission(user):
    # this function check if user has the permission to grant permission to anotehr user
    # for example a user with permission of certain program will be able to add permission of
    # all schedule under this program to another user
    profile = get_user_profile(user)
    zone_perm = profile.zone_permission.all()
    program_perm = profile.program_permission.all()
    perm_set = {}
    if user.is_superuser:
        perm_set['zone_set'] = Zone.objects.all()
        perm_set['program_set'] = Program.objects.all()
        perm_set['schedule_set'] = Schedule.objects.all()
    else:
        perm_set['zone_set'] = Zone.objects.none()
        perm_set['program_set'] = Program.objects.filter(zone__in=zone_perm)
        perm_set['schedule_set'] = Schedule.objects.filter(Q(program__in=program_perm) |
                                                           Q(program__zone__in=zone_perm)).distinct()
    perm_set['session_perm'] = profile.session_permission or user.is_superuser
    perm_set['school_perm'] = profile.school_permission or user.is_superuser
    perm_set['student_perm'] = profile.student_permission or user.is_superuser
    perm_set['partner_perm'] = profile.partner_permission or user.is_superuser
    return perm_set


@require_http_methods(["GET", "POST"])
@login_required
def add_user_view(request):
    if request.method == "GET":
        add_user_form = AddUserForm()
        return render(request, "accounts_add_user.html", {'add_user_form': add_user_form})
    else:
        add_user_form = AddUserForm(request.POST)
        if add_user_form.is_valid():
            add_user_form.save()
            return render(request, "accounts_add_user.html", {'add_user_form': add_user_form, 'success': True})
        else:
            return render(request, "accounts_add_user.html", {'add_user_form': add_user_form})


def set_other_perm_fields(add_user_perm_form, perm_set):
    # if user doesnt have certain non-level permission we disable relative widgets
    add_user_perm_form.fields['session_permission'].widget.attrs['disabled'] = not perm_set['session_perm']
    add_user_perm_form.fields['school_permission'].widget.attrs['disabled'] = not perm_set['school_perm']
    add_user_perm_form.fields['student_permission'].widget.attrs['disabled'] = not perm_set['student_perm']
    add_user_perm_form.fields['partner_permission'].widget.attrs['disabled'] = not perm_set['partner_perm']


@require_http_methods(["GET"])
@login_required
def get_user_perm_view(request):
    # this view is for ajax to retrieve target user's permission when the user select input changed
    perm_set = get_user_permission(request.user)
    add_user_perm_form = UserPermForm(instance=get_user_profile(get_object_or_404(User, id=request.GET['user'])),
                                      **perm_set)
    set_other_perm_fields(add_user_perm_form, perm_set)
    request_context = csrf(request)
    form_html = render_crispy_form(add_user_perm_form, context=request_context)
    return HttpResponse(json.dumps({'form_html': form_html}))


@require_http_methods(["GET", "POST"])
@login_required
def add_user_perm_view(request):
    perm_set = get_user_permission(request.user)
    if request.method == "GET":
        add_user_perm_form = UserPermForm(**perm_set)
        set_other_perm_fields(add_user_perm_form, perm_set)
        return render(request, "accounts_add_user_perm.html", {'add_user_perm_form': add_user_perm_form})
    else:
        query_dict = request.POST
        # if no user is selected we make target profile in the form to be none so it won't get a 404 error
        # and is able to return a required field error message
        if query_dict.get('user') == "":
            add_user_perm_form = UserPermForm(data=query_dict, **perm_set)
            target_profile = UserProfile.objects.none()
        else:
            target_profile = get_user_profile(get_object_or_404(User, id=query_dict.get('user')))
            add_user_perm_form = UserPermForm(instance=target_profile, data=query_dict, **perm_set)
        set_other_perm_fields(add_user_perm_form, perm_set)
        # get target user's non-level permission
        session_permission = target_profile.session_permission
        school_permission = target_profile.school_permission
        student_permission = target_profile.student_permission
        partner_permission = target_profile.partner_permission
        if add_user_perm_form.is_valid():
            # depending on user's permission some non-level permission widgets may be disabled
            # and the queryset doesnt have permission that the user can't gran to target user
            # we first get the object the form will save to, but dont save it
            form_obj = add_user_perm_form.save(commit=False)
            # then we manually adjust the target user's permission or profile, then save it
            form_obj.zone_permission = \
                Zone.objects.filter(Q(id__in=add_user_perm_form.cleaned_data['zone_permission']) |
                                    Q(id__in=target_profile.zone_permission.exclude(id__in=perm_set['zone_set'].
                                                                                    values('id'))))
            form_obj.program_permission = \
                Program.objects.filter(Q(id__in=add_user_perm_form.cleaned_data['program_permission']) |
                                       Q(id__in=target_profile.program_permission.exclude
                                       (id__in=perm_set['program_set'].values('id'))))
            form_obj.schedule_permission = \
                Schedule.objects.filter(Q(id__in=add_user_perm_form.cleaned_data['schedule_permission']) |
                                        Q(id__in=target_profile.schedule_permission.exclude
                                        (id__in=perm_set['schedule_set'].values('id'))))
            if not perm_set['session_perm']:
                form_obj.session_permission = session_permission
            if not perm_set['school_perm']:
                form_obj.school_permission = school_permission
            if not perm_set['student_perm']:
                form_obj.student_permission = student_permission
            if not perm_set['partner_perm']:
                form_obj.partner_permission = partner_permission
            form_obj.save()
            add_user_perm_form = UserPermForm(instance=target_profile, **perm_set)
            return render(request, "accounts_add_user_perm.html", {'add_user_perm_form': add_user_perm_form,
                                                                   'success': True})
        else:
            return render(request, "accounts_add_user_perm.html", {'add_user_perm_form': add_user_perm_form})
