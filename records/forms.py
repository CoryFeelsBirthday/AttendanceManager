from django import forms
from crispy_forms.helper import FormHelper


class CrispyRecordForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CrispyRecordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'record_form'
        self.helper.form_method = 'post'
        for disabled in self.disabled_fields:
            self.fields[disabled].widget.attrs['disabled'] = True

    class Meta:
        pass


def crispy_form_factory(model, widgets, disabled, exclude, form=CrispyRecordForm):
    # this factory is able to create a crispy bootstrap form for ajax request
    parent = (form, object)
    Meta = type(str('Meta'), parent, {"model": model, 'exclude': exclude, 'widgets': widgets})
    class_name = model.__name__ + "CrispyForm"
    return type(class_name, parent, {"Meta": Meta, 'disabled_fields': disabled})


class DeleteForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(DeleteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'record_form'
        self.helper.form_method = 'post'
