from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import index, MissionBoardHome

urlpatterns = [
    url(r'^$', MissionBoardHome.as_view(), name="mission_board_home"),
    url(r'^$', index, name="index"),
]
