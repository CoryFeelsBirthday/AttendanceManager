from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from django import forms


class ProfileForm(forms.Form):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    phone_number = forms.CharField(max_length=20, required=False)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_action = ''
        self.helper.add_input(Submit('save_change', 'Save Change'))


class AddUserForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_action = ''
        self.helper.add_input(Submit('add_user', 'Add User'))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'date_joined']
        widgets = {
            'date_joined': forms.HiddenInput()
        }


class UserPermForm(forms.ModelForm):

    def __init__(self, zone_set, program_set, schedule_set, session_perm, school_perm, student_perm, partner_perm, *args, **kwargs):
        super(UserPermForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'user_perm_form'
        self.helper.form_method = 'POST'
        self.helper.form_action = ''
        self.helper.add_input(Submit('add_perm', 'Add Permission'))
        # Assign queryset for multi choice field when creating form
        self.fields['zone_permission'] = forms.ModelMultipleChoiceField(queryset=zone_set, required=False)
        self.fields['program_permission'] = forms.ModelMultipleChoiceField(queryset=program_set, required=False)
        self.fields['schedule_permission'] = forms.ModelMultipleChoiceField(queryset=schedule_set, required=False)

    class Meta:
        model = UserProfile
        fields = ['user', 'zone_permission', 'program_permission', 'schedule_permission', 'session_permission',
                  'school_permission', 'student_permission', 'partner_permission', ]
