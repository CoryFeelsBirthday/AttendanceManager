from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Zone, Program, Schedule, Enrollment, Attendance, CanceledDate, Student, Session, School, Partner
from django.db.models import Q
from urllib.parse import unquote
from django.http import HttpResponse
import json
from crispy_forms.utils import render_crispy_form
from .forms import DeleteForm, crispy_form_factory
from django.core.context_processors import csrf
import datetime
from django.forms import modelformset_factory
from django import forms
from accounts.models import get_user_profile
model_name_dict = {
    'zone': Zone,
    'program': Program,
    'schedule': Schedule,
    'enrollment': Enrollment,
    'canceled_date': CanceledDate,
    'session': Session,
    'student': Student,
    'school': School,
    'partner': Partner
}

higher_model_name_dict = {
    'zone': None,
    'program': 'zone',
    'schedule': 'program',
    'enrollment': 'schedule',
    'canceled_date': 'schedule'
}


def get_objs_and_perm(user, **kwargs):
    # this function is to find the users permission for current page
    # given following record architecture
    # zone1-program1-schedule1
    # if a user has permission of program1 he will be able to see zone1 in zone page,
    # he is also able to see program1 in program page, however he doesnt have permission to edit zone1 or program1
    # but he is able to edit schedule1 in schedule page,
    # if zone1 has another program called program2, he is not able to see it.

    res_map = {}
    perm = user.is_superuser
    profile = get_user_profile(user)

    # depending the page user is requesting, we will have a list of obj as argument

    if 'zone_name' in kwargs:
        # user is requesting program page
        zone_name = unquote(kwargs['zone_name'])
        zone = Zone.objects.get(name=zone_name)
        perm = perm or profile.zone_permission.filter(id=zone.id).exists()
        res_map.update({'zone': zone})
        if 'program_name' in kwargs:
            # user is requesting schedule page
            program_name = unquote(kwargs['program_name'])
            program = Program.objects.get(name=program_name, zone=zone)
            perm = perm or profile.program_permission.filter(id=program.id).exists()
            res_map.update({'program': program})
            if 'session_name' in kwargs:
                # user is requesting enrollment page or canceled_date page
                session_name = unquote(kwargs['session_name'])
                schedule = Schedule.objects.get(program=program, session__name=session_name)
                perm = perm or profile.schedule_permission.filter(id=schedule.id).exists()
                res_map.update({'schedule': schedule})
                if 'student_id' in kwargs:
                    student_id = kwargs['student_id']
                    enrollment = get_object_or_404(Enrollment, schedule=schedule, student__id=student_id)
                    res_map.update({'enrollment': enrollment})
                if 'canceled_date' in kwargs:
                    canceled_date = kwargs['canceled_date']
                    canceled_date = get_object_or_404(CanceledDate, schedule=schedule, date=canceled_date)
                    res_map.update({'canceled_date': canceled_date})

    # we return a dict of objects representing this page. i.e. user is requesting a schedule page,
    # we will return the zone and program of these schedules we are about to show

    res_map.update({'perm': perm})
    return res_map


def update_context(query_set, perm, **kwargs):
    context = {'query_set': query_set, 'perm': perm}
    context.update(kwargs)
    return context

# these views are used to get the corresponding records that user is able to see
# return these records also return a bool indicate if the user has permission to edit them


@require_http_methods(["GET"])
@login_required
def zone_view(request, **kwargs):
    objs_and_perm = get_objs_and_perm(request.user)
    profile = get_user_profile(request.user)
    if objs_and_perm['perm']:
        query_set = Zone.objects.all()
    else:
        query_set = Zone.objects.filter(
            Q(id__in=profile.zone_permission.all().values('id')) |
            Q(program__in=profile.program_permission.all()) |
            Q(program__schedule__in=profile.schedule_permission.all())
        ).distinct()

    context = update_context(query_set, objs_and_perm['perm'], **kwargs)
    return render(request, "records_zone.html", context)


@require_http_methods(["GET"])
@login_required
def program_view(request, **kwargs):
    objs_and_perm = get_objs_and_perm(request.user, **kwargs)
    profile = get_user_profile(request.user)
    if objs_and_perm['perm']:
        query_set = Program.objects.filter(zone=objs_and_perm['zone'])
    else:
        query_set = Program.objects.filter(
            Q(id__in=profile.program_permission.filter(zone=objs_and_perm['zone']).values('id')) |
            Q(schedule__in=profile.schedule_permission.filter(program__zone=objs_and_perm['zone']))
        ).distinct()
    context = update_context(query_set, objs_and_perm['perm'], **kwargs)
    return render(request, "records_program.html", context)


@require_http_methods(["GET"])
@login_required
def schedule_view(request, **kwargs):
    objs_and_perm = get_objs_and_perm(request.user, **kwargs)
    profile = get_user_profile(request.user)
    if objs_and_perm['perm']:
        query_set = Schedule.objects.filter(program=objs_and_perm['program'])
    else:
        query_set = profile.schedule_permission.filter(program=objs_and_perm['program'])
    context = update_context(query_set, objs_and_perm['perm'], **kwargs)
    return render(request, "records_schedule.html", context)


@require_http_methods(["GET"])
@login_required
def enrollment_view(request, **kwargs):
    objs_and_perm = get_objs_and_perm(request.user, **kwargs)
    if objs_and_perm['perm']:
        query_set = Enrollment.objects.filter(schedule=objs_and_perm['schedule'])
    else:
        query_set = Enrollment.objects.none()
    today = datetime.date.today().strftime('%Y-%m-%d')
    context = update_context(query_set, objs_and_perm['perm'], **kwargs)
    context.update({'today': today})
    return render(request, "records_enrollment.html", context)


@require_http_methods(["GET"])
@login_required
def canceled_date_view(request, **kwargs):
    objs_and_perm = get_objs_and_perm(request.user, **kwargs)
    if objs_and_perm['perm']:
        query_set = CanceledDate.objects.filter(schedule=objs_and_perm['schedule'])
    else:
        query_set = CanceledDate.objects.none()
    context = update_context(query_set, objs_and_perm['perm'], **kwargs)
    return render(request, "records_canceled_date.html", context)


@require_http_methods(["GET", "POST"])
@login_required
def attendance_view(request, **kwargs):

    # attendance view return a formset of all attendance of the enrollment of
    # a certain schedule and a certain date, user will be able to submit this formset

    objs_and_perm = get_objs_and_perm(request.user, **kwargs)
    schedule = objs_and_perm['schedule']
    date = kwargs['date']
    date = date.split('-')
    date = datetime.date(int(date[0]), int(date[1]), int(date[2]))

    # in the date picker we only enable the dates that are not in invalid dates,
    # these invalid dates include the canceled date, the weekdays not in the schedule
    # and the date are out of schedule's start end date range

    canceled_dates = CanceledDate.objects.filter(schedule=schedule).values_list('date', flat=True)
    date_valid = date not in canceled_dates
    start_date = schedule.session.start_date
    end_date = schedule.session.end_date
    date_valid = date_valid and date >= start_date and date <= end_date
    meeting_days = schedule.meeting_day
    week_days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    date_valid = date_valid and (week_days[date.weekday()] in meeting_days)
    week_disabled = ""
    for idx, weekday in enumerate(week_days):
        if weekday not in meeting_days:
            week_disabled += str(idx)

    if request.method == "GET":
        # we only get the enrollment list if user has permission and the date is valid
        if objs_and_perm['perm'] and date_valid:
            enrollment_query_set = Enrollment.objects.filter(schedule=schedule). \
                exclude(start_date__gt=date). \
                exclude(end_date__lt=date)
            for enroll in enrollment_query_set:
                Attendance.objects.get_or_create(enrollment=enroll, date=date)
            attendance_set = Attendance.objects.filter(enrollment__in=enrollment_query_set, date=date)
        else:
            attendance_set = Attendance.objects.none()

        formset_class = modelformset_factory(Attendance,
                                             fields="__all__",
                                             widgets={'attendance_status':
                                                      forms.widgets.Select()},
                                             max_num=0)
        formset = formset_class(queryset=attendance_set)
        context = {'formset': formset,
                   'canceled_dates': canceled_dates,
                   'start_date': start_date,
                   'end_date': end_date,
                   'week_disabled': week_disabled
                   }
        context.update(kwargs)

        return render(request, "records_attendance.html", context)

    if request.method == "POST":
        if objs_and_perm['perm'] and date_valid:
            formset_class = modelformset_factory(Attendance,
                                                 fields="__all__",
                                                 widgets={'attendance_status':
                                                          forms.widgets.Select(choices=Attendance.STATUS_TYPE)},
                                                 max_num=0)
            formset = formset_class(request.POST)
            if formset.is_valid():
                formset.save()
            context = {'formset': formset,
                       'canceled_dates': canceled_dates,
                       'start_date': start_date,
                       'end_date': end_date,
                       'week_disabled': week_disabled
                       }
            context.update(kwargs)

            return render(request, "records_attendance.html", context)
        else:
            if not objs_and_perm['perm']:
                return HttpResponse("You don't have permission")
            else:
                return HttpResponse("Selected date is invalid")


widgets_dict = {'zone': {},
                'program': {},
                'schedule': {},
                'enrollment': {'start_date': forms.DateInput(attrs={'placeholder': 'yyyy-mm-dd'}),
                               'end_date': forms.DateInput(attrs={'placeholder': 'yyyy-mm-dd'})
                               },
                'canceled_date': {'date': forms.DateInput(attrs={'placeholder': 'yyyy-mm-dd'})},
                'session': {'start_date': forms.DateInput(attrs={'placeholder': 'yyyy-mm-dd'}),
                            'end_date': forms.DateInput(attrs={'placeholder': 'yyyy-mm-dd'})
                            },
                'student': {'dob': forms.DateInput(attrs={'placeholder': 'yyyy-mm-dd'})},
                'school': {},
                'partner': {},
                }


@require_http_methods(["GET", "POST"])
@login_required
def add_view(request, model_name, **kwargs):

    # this view is for ajax to fetch add_form of a certain leveled model

    objs_and_perm = get_objs_and_perm(request.user, **kwargs)
    higher_model_name = higher_model_name_dict[model_name]
    if higher_model_name is None:
        disabled = []
    else:
        disabled = [higher_model_name]
    form_class = crispy_form_factory(model=model_name_dict[model_name],
                                     widgets=widgets_dict[model_name],
                                     disabled=disabled,
                                     exclude=[],
                                     )
    if request.method == 'GET':
        add_form = form_class(initial={higher_model_name: objs_and_perm.get(higher_model_name)})
        request_context = csrf(request)
        form_html = render_crispy_form(add_form, context=request_context)
        return HttpResponse(json.dumps({'form_html': form_html}))

    if request.method == 'POST':
        if objs_and_perm['perm']:
            POST = request.POST.copy()
            if higher_model_name is not None:
                POST[higher_model_name] = objs_and_perm.get(higher_model_name).id
            add_form = form_class(POST)
            if add_form.is_valid():
                add_form.save()
                return HttpResponse(json.dumps({'success': True}))
            else:
                request_context = csrf(request)
                form_html = render_crispy_form(add_form, context=request_context)
                return HttpResponse(json.dumps({'success': False, 'permission': True, 'form_html': form_html}))
        else:
            return HttpResponse(json.dumps({'success': False, 'permission': False}))


@require_http_methods(["GET", "POST"])
@login_required
def edit_view(request, model_name, **kwargs):
    objs_and_perm = get_objs_and_perm(request.user, **kwargs)
    higher_model_name = higher_model_name_dict[model_name]
    if higher_model_name is None:
        disabled = []
    else:
        disabled = [higher_model_name]
    form_class = crispy_form_factory(model=model_name_dict[model_name],
                                     widgets=widgets_dict[model_name],
                                     disabled=disabled,
                                     exclude=[],
                                     )

    if request.method == 'GET':
        edit_form = form_class(instance=objs_and_perm[model_name])
        request_context = csrf(request)
        form_html = render_crispy_form(edit_form, context=request_context)
        return HttpResponse(json.dumps({'form_html': form_html}))

    if request.method == 'POST':
        if objs_and_perm['perm']:
            POST = request.POST.copy()
            if higher_model_name is not None:
                POST[higher_model_name] = objs_and_perm.get(higher_model_name).id
            edit_form = form_class(POST, instance=objs_and_perm[model_name])
            if edit_form.is_valid():
                edit_form.save()
                return HttpResponse(json.dumps({'success': True}))
            else:
                request_context = csrf(request)
                form_html = render_crispy_form(edit_form, context=request_context)
                return HttpResponse(json.dumps({'success': False, 'permission': True, 'form_html': form_html}))
        else:
            return HttpResponse(json.dumps({'success': False, 'permission': False}))


@require_http_methods(["GET", "POST"])
@login_required
def delete_view(request, model_name, **kwargs):

    # deleting uses the cascading
    objs_and_perm = get_objs_and_perm(request.user, **kwargs)
    if request.method == 'GET':
        delete_form = DeleteForm()
        request_context = csrf(request)
        form_html = render_crispy_form(delete_form, context=request_context)
        return HttpResponse(json.dumps({'form_html': "<p>You are going to delete following record: <strong>" +
                                                     str(objs_and_perm[model_name]) + "</strong></p>" + form_html}))
    if request.method == 'POST':
        if objs_and_perm['perm']:
            delete_form = DeleteForm(request.POST)
            if delete_form.is_valid():
                objs_and_perm[model_name].delete()
                return HttpResponse(json.dumps({'success': True, 'permission': True}))
        else:
            return HttpResponse(json.dumps({'success': False, 'permission': False}))


@require_http_methods(["GET"])
@login_required
def session_view(request, **kwargs):
    profile = get_user_profile(request.user)
    perm = profile.session_permission or request.user.is_superuser
    query_set = Session.objects.all()
    return render(request, "records_session.html", {'perm': perm, 'query_set': query_set})


@require_http_methods(["GET"])
@login_required
def student_view(request, **kwargs):
    profile = get_user_profile(request.user)
    perm = profile.student_permission or request.user.is_superuser
    query_set = Student.objects.all()
    return render(request, "records_student.html", {'perm': perm, 'query_set': query_set})


@require_http_methods(["GET"])
@login_required
def school_view(request, **kwargs):
    profile = get_user_profile(request.user)
    perm = profile.school_permission or request.user.is_superuser
    query_set = School.objects.all()
    return render(request, "records_school.html", {'perm': perm, 'query_set': query_set})


@require_http_methods(["GET"])
@login_required
def partner_view(request, **kwargs):
    profile = get_user_profile(request.user)
    perm = profile.partner_permission or request.user.is_superuser
    query_set = Partner.objects.all()
    return render(request, "records_partner.html", {'perm': perm, 'query_set': query_set})


@require_http_methods(["GET", "POST"])
@login_required
def others_add_view(request, model_name):

    # this view is for non-leveled model

    perm = getattr(get_user_profile(request.user), model_name + '_permission') or request.user.is_superuser
    form_class = crispy_form_factory(model=model_name_dict[model_name],
                                     widgets=widgets_dict[model_name],
                                     disabled=[],
                                     exclude=[],
                                     )
    if request.method == 'GET':
        add_form = form_class()
        request_context = csrf(request)
        form_html = render_crispy_form(add_form, context=request_context)
        return HttpResponse(json.dumps({'form_html': form_html}))

    if request.method == 'POST':
        if perm:
            add_form = form_class(request.POST)
            if add_form.is_valid():
                add_form.save()
                return HttpResponse(json.dumps({'success': True}))
            else:
                request_context = csrf(request)
                form_html = render_crispy_form(add_form, context=request_context)
                return HttpResponse(json.dumps({'success': False, 'permission': True, 'form_html': form_html}))
        else:
            return HttpResponse(json.dumps({'success': False, 'permission': False}))


@require_http_methods(["GET", "POST"])
@login_required
def others_edit_view(request, model_name, **kwargs):

    perm = getattr(get_user_profile(request.user), model_name + '_permission') or request.user.is_superuser
    form_class = crispy_form_factory(model=model_name_dict[model_name],
                                     widgets=widgets_dict[model_name],
                                     disabled=[],
                                     exclude=[],
                                     )

    if request.method == 'GET':
        edit_form = form_class(instance=get_object_or_404(model_name_dict[model_name], id=kwargs['id']))
        request_context = csrf(request)
        form_html = render_crispy_form(edit_form, context=request_context)
        return HttpResponse(json.dumps({'form_html': form_html}))

    if request.method == 'POST':
        if perm:
            edit_form = form_class(request.POST, instance=get_object_or_404(model_name_dict[model_name],
                                                                            id=kwargs['id']))
            if edit_form.is_valid():
                edit_form.save()
                return HttpResponse(json.dumps({'success': True}))
            else:
                request_context = csrf(request)
                form_html = render_crispy_form(edit_form, context=request_context)
                return HttpResponse(json.dumps({'success': False, 'permission': True, 'form_html': form_html}))
        else:
            return HttpResponse(json.dumps({'success': False, 'permission': False}))


@require_http_methods(["GET", "POST"])
@login_required
def others_delete_view(request, model_name, **kwargs):

    perm = getattr(get_user_profile(request.user), model_name + '_permission') or request.user.is_superuser
    obj = get_object_or_404(model_name_dict[model_name], id=kwargs['id'])
    if request.method == 'GET':
        delete_form = DeleteForm()
        request_context = csrf(request)
        form_html = render_crispy_form(delete_form, context=request_context)
        return HttpResponse(json.dumps({'form_html': "<p>You are going to delete following record: <strong>" +
                                                     str(obj) + "</strong></p>" + form_html}))
    if request.method == 'POST':
        if perm:
            delete_form = DeleteForm(request.POST)
            if delete_form.is_valid():
                obj.delete()
                return HttpResponse(json.dumps({'success': True, 'permission': True}))
        else:
            return HttpResponse(json.dumps({'success': False, 'permission': False}))
