from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import submit_flag, team_stats, Scoreboard, \
    TracksList, MissionPage, csadmin_index, TrackDetail, GlobalAnnouncementList

urlpatterns = [
    url(r'^cs_admin/$', csadmin_index, name="csadmin_index"),

    url(r'^flag/$', submit_flag, name="submit_flag"),
    url(r'^team/(?P<team_id>\w+)$', team_stats, name="team_stats"),
    url(r'^track/(?P<pk>\w+)$', TrackDetail.as_view(), name="track_detail"),
    url(r'^mission/(?P<mission>\w+)$', MissionPage.as_view(), name="mission_page"),
    url(r'^scoreboard/$', Scoreboard.as_view(), name="scoreboard"),
    url(r'^announcements/$', GlobalAnnouncementList.as_view(), name="announcements"),
    # url(r'^missions$', TracksList.as_view(), name="tracklist"),
    url(r'^$', TracksList.as_view(), name="tracklist"),
]
