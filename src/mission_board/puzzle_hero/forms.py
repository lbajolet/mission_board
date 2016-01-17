from django import forms
from django.core.urlresolvers import reverse_lazy
from django.forms import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Flag, Submission


class FlagField(forms.CharField):

    def to_python(self, value):
        if not value:
            return ""
        return value

    def validate(self, value):

        super(FlagField, self).validate(value)
        queryset = Flag.objects.filter(token=value).first()

        if not queryset:
            raise ValidationError(
                'Invalid flag: %(value)s',
                code='invalid_flag',
                params={'value': value},
            )


class FlagSubmissionForm(forms.Form):
    token = FlagField(
        max_length=255,
        label="Flag",
        widget=forms.TextInput(
            attrs={'placeholder': 'FLAG_123456789'}
        )
    )

    def __init__(self, *args, **kwargs):
        super(FlagSubmissionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse_lazy('submit_flag')
        self.helper.add_input(Submit('submit', 'Submit'))
