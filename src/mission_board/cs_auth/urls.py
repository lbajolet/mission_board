from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import LoginView, LogoutView, RegisterView, ProfileView, \
    EditProfileView

urlpatterns = [
    url(r'^login$', LoginView.as_view(), name="login"),
    url(r'^logout$', login_required(LogoutView.as_view()), name="logout"),
    url(r'^register$', RegisterView.as_view(), name="register"),
    url(r'^edit_profile$', EditProfileView.as_view(), name="edit_profile"),
    url(r'^profile/(?P<pk>\w+)$', ProfileView.as_view(), name="profile"),
]
