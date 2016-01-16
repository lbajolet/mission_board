from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import submit_flag, team_stats, MissionBoardHome, MissionBoardMission, MissionBoardTeams

urlpatterns = [
    url(r'^teams$', MissionBoardTeams.as_view(), name="mission_board_teams"),
    url(r'^team_stats$', team_stats, name="team_stats"),
    url(r'^missions/(?P<mission>\w+)$', MissionBoardMission.as_view(), name="mission_board_mission"),
    url(r'^flag/$', submit_flag, name="submit_flag"),
    url(r'^$', MissionBoardHome.as_view(), name="mission_board_home"),
]
