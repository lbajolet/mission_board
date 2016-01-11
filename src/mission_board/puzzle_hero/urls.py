from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import index

urlpatterns = [
    url(r'^$', index, name="index"),
]
