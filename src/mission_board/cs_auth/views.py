import os

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

    def form_valid(self, form):
        user = self.request.user
        if form.cleaned_data.get("display_name", None):
            user.player.display_name = form.cleaned_data.get("display_name")
        if form.cleaned_data.get("email", None):
            user.email = form.cleaned_data.get("email")
        if form.cleaned_data.get("first_name", None):
            user.first_name = form.cleaned_data.get("first_name")
        if form.cleaned_data.get("last_name", None):
            user.last_name = form.cleaned_data.get("last_name")
        if form.cleaned_data.get("curriculum_vitae", None):
            path = self._handle_pdf(form.cleaned_data.get("curriculum_vitae"))
            user.player.curriculum_vitae = path
        user.player.save()
        user.save()

        return super(EditProfileView, self).form_valid(form)

    def _handle_pdf(self, data):
        filepath = 'cv/%s/%s_%s.pdf' % (self.request.user.player.team.name,
                                        self.request.user.first_name,
                                        self.request.user.last_name)

        filepath = os.path.join(settings.MEDIA_ROOT, filepath)
        dirpath = os.path.dirname(filepath)
        print(dirpath)

        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)

        filepath = os.path.join(dirpath, filepath)
        print(filepath)
        with open(filepath, 'wb') as fd:
            for chunk in data.chunks():
                fd.write(chunk)

        return filepath


class ProfileView(DetailView):
    model = User
    template_name = "cs_auth/profile.html"

