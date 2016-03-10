import os

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Player, Team
from .validators import team_exists


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('submit', 'Login'))
        self.fields['username'].widget.attrs.update({
            'autocapitalize': 'none'
        })

    class Meta:
        model = User


class RegisterForm(UserCreationForm):
    team_token = forms.CharField(
        max_length=32,
        required=True,
        help_text=('Your team leader has received '
                   'this by email prior to the '
                   'competition'),
        validators=[team_exists]
    )

    email = forms.EmailField(
        max_length=75,
        required=True,
        label="Email address",
        )

    first_name = forms.CharField(
        max_length=64,
        required=True,
        )

    last_name = forms.CharField(
        max_length=64,
        required=True,
        )

    class Meta:
        model = User
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',
                  'password1',
                  'password2',
                  )

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('submit', 'Register'))
        self.fields['username'].widget.attrs.update({
            'autocapitalize': 'none'
        })

    def save(self, commit=True):
        super(RegisterForm, self).save(commit=commit)
        username = self.cleaned_data['username']
        team_token = self.cleaned_data['team_token']
        user = User.objects.get_by_natural_key(username)
        team = Team.objects.filter(token=team_token)[0]
        player = Player.objects.create(
            user=user,
            team=team,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.username,
        )

        if commit:
            player.save()


class PDFField(forms.FileField):

    def clean(self, *args, **kwargs):
        data = super(PDFField, self).clean(*args, **kwargs)
        if data:
            filename = data.name
            ext = os.path.splitext(filename)[1]
            ext = ext.lower()
            if ext != ".pdf":
                raise forms.ValidationError("Only PDF files are allowed!")


class ProfileForm(forms.Form):

    display_name = forms.CharField(max_length=128, required=False)
    email = forms.EmailField(
        max_length=75,
        required=False,
        label="Email address",
    )

    first_name = forms.CharField(
        max_length=64,
        required=False,
        )

    last_name = forms.CharField(
        max_length=64,
        required=False,
    )

    curriculum_vitae = PDFField(
        required=False,
        max_length=20000,
        help_text="*.pdf only!"
    )

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('submit', 'Update Profile'))

