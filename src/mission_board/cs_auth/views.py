from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.views import logout
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView


from .forms import LoginForm, RegisterForm, ProfileForm
from .models import Player


class LoginView(SuccessMessageMixin, FormView):
    template_name = "cs_auth/form_view.html"
    form_class = LoginForm
    success_url = "/"
    success_message = "Successfully logged in!"

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)


class LogoutView(RedirectView):
    url = settings.LOGIN_URL
    permanent = True
    success_message = "Logged out!"

    def dispatch(self, request, *args, **kwargs):
        logout(self.request)
        return super(LogoutView, self).dispatch(request, *args, **kwargs)


class RegisterView(SuccessMessageMixin, FormView):
    template_name = "cs_auth/form_view.html"
    form_class = RegisterForm
    success_url = "/"
    success_message = "Successfully registered!"

    def form_valid(self, form):
        form.save()
        return super(RegisterView, self).form_valid(form)


class EditProfileView(SuccessMessageMixin, FormView):
    form_class = ProfileForm
    template_name = "cs_auth/form_view.html"
    success_message = "Profile successfully updated!"

    def get_success_url(self):
        return "/auth/profile/" + str(self.request.user.id)


class ProfileView(DetailView):
    model = User
    template_name = "cs_auth/profile.html"

