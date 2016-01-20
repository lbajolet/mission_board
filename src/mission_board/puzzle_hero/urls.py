from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import submit_flag, team_stats, Scoreboard, MissionBoardHome, MissionBoardMission

urlpatterns = [
    url(r'^team_stats$', team_stats, name="team_stats"),
    url(r'^missions/(?P<mission>\w+)$', MissionBoardMission.as_view(), name="mission_board_mission"),
    url(r'^flag/$', submit_flag, name="submit_flag"),
    url(r'^$', Scoreboard.as_view(), name="scoreboard"),
]
