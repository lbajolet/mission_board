from django import forms

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
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
