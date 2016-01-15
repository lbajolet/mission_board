from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import index, MissionBoardHome, MissionBoardMission

urlpatterns = [
    url(r'^missions/(?P<mission>\w+)$', MissionBoardMission.as_view(), name="mission_board_mission"),
    url(r'^$', MissionBoardHome.as_view(), name="mission_board_home"),
    url(r'^$', index, name="index"),
]
