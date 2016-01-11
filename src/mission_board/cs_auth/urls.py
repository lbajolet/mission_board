from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import LoginView, LogoutView, RegisterView

urlpatterns = [
    url(r'^login$', LoginView.as_view(), name="login"),
    url(r'^logout$', login_required(LogoutView.as_view()), name="logout"),
    url(r'^register$', RegisterView.as_view(), name="register"),
]
