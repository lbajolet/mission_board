from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import submit_flag, team_stats, Scoreboard, TracksList, MissionPage

urlpatterns = [
    url(r'^team_stats$', team_stats, name="team_stats"),
    url(r'^flag/$', submit_flag, name="submit_flag"),
    url(r'^missions/(?P<mission>\w+)$', MissionPage.as_view(), name="mission_page"),
    url(r'^missions$', TracksList.as_view(), name="tracklist"),
    url(r'^$', Scoreboard.as_view(), name="scoreboard"),
]
