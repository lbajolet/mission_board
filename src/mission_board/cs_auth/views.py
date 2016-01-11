from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.views import logout
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import RedirectView
from django.views.generic.edit import FormView

from .forms import LoginForm, RegisterForm


class LoginView(FormView):
    template_name = "cs_auth/form_view.html"
    form_class = LoginForm
    success_url = "/"
    success_message = ("Successfully logged in as "
                       "%(first_name)s %(last_name)s."
                       "(%(username)s).")

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data,
                                           first_name=self.object.first_name,
                                           last_name=self.object.last_name,
                                           username=self.object.username)


class LogoutView(RedirectView):
    url = settings.LOGIN_URL
    permanent = True

    def dispatch(self, request, *args, **kwargs):
        logout(self.request)
        return super(LogoutView, self).dispatch(request, *args, **kwargs)


class RegisterView(FormView):
    template_name = "cs_auth/form_view.html"
    form_class = RegisterForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        return super(RegisterView, self).form_valid(form)
