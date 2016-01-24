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

    def save(self, commit=True):
        super(RegisterForm, self).save(commit=commit)
        username = self.cleaned_data['username']
        team_token = self.cleaned_data['team_token']
        user = User.objects.get_by_natural_key(username)
        team = Team.objects.filter(token=team_token)[0]
        player = Player.objects.create(user=user, team=team)
        if commit:
            player.save()


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

    curriculum_vitae = forms.FileField(required=False, max_length=20000)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('submit', 'Update Profile'))

    def save(self, commit=True):
        super(ProfileForm, self).save(commit=commit)
        user = self.request.user
        if self.cleaned_data.get("display_name", None):
            user.player.display_name = self.cleaned_data.get("display_name")
        if self.cleaned_data.get("email", None):
            user.email = self.cleaned_data.get("email")
        if self.cleaned_data.get("first_name", None):
            user.first_name = self.cleaned_data.get("first_name")
        if self.cleaned_data.get("last_name", None):
            user.last_name = self.cleaned_data.get("last_name")
        if self.cleaned_data.get("curriculum_vitae", None):
            # TODO handle pdf files here
            user.player.curriculum_vitae = self.cleaned_data.\
                get("curriculum_vitae")
        if commit:
            user.player.save()
            user.save()
