from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import submit_flag, team_stats, Scoreboard, \
    TracksList, MissionPage, csadmin_index, TrackDetail, GlobalAnnouncementList, \
    admin_dashboard, global_status_ok, global_status_scoreboard

urlpatterns = [
    url(r'^cs_admin/$', csadmin_index, name="csadmin_index"),

    url(r'^flag/$', global_status_ok(submit_flag), name="submit_flag"),
    url(r'^team/(?P<team_id>\w+)$', global_status_scoreboard(team_stats), name="team_stats"),
    url(r'^track/(?P<pk>\w+)$', global_status_ok(TrackDetail.as_view()), name="track_detail"),
    url(r'^mission/(?P<mission>\w+)$', global_status_ok(MissionPage.as_view()), name="mission_page"),
    url(r'^scoreboard/$', global_status_scoreboard(Scoreboard.as_view()), name="scoreboard"),
    url(r'^announcements/$', GlobalAnnouncementList.as_view(), name="announcements"),
    url(r'^admin_dashboard/$', admin_dashboard, name="admin_dashboard"),
    url(r'^$', global_status_ok(TracksList.as_view()), name="tracklist"),
]
