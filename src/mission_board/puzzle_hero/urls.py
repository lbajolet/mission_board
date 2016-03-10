from django.conf.urls import url

from .views import submit_flag, team_stats, Scoreboard, \
    TracksList, MissionPage, admin_panel, TrackDetail, GlobalAnnouncementList, \
    admin_dashboard, global_status_ok, global_status_scoreboard, \
    admin_submit_flag, admin_global_submit_flag, MobileTrackList

urlpatterns = [
    url(r'^cs_admin/$', admin_panel, name="admin_panel"),
    url(r'^admin_dashboard/$', admin_dashboard, name="dashboard"),
    url(r'^admin_flag/$', admin_submit_flag, name="admin_submit_flag"),
    url(r'^admin_global_flag/$', admin_global_submit_flag, name="admin_global_submit_flag"),

    url(r'^flag/$', global_status_ok(submit_flag), name="submit_flag"),
    url(r'^team/(?P<team_id>\w+)$', global_status_scoreboard(team_stats), name="team_stats"),
    url(r'^track/(?P<pk>\w+)$', global_status_ok(TrackDetail.as_view()), name="track_detail"),
    url(r'^mission/(?P<mission>\w+)$', global_status_ok(MissionPage.as_view()), name="mission_page"),
    url(r'^scoreboard/$', global_status_scoreboard(Scoreboard.as_view()), name="scoreboard"),
    url(r'^announcements/$', GlobalAnnouncementList.as_view(), name="announcements"),
    url(r'^mobile$', global_status_ok(MobileTrackList.as_view()), name="mobile_tracklist"),
    url(r'^$', global_status_ok(TracksList.as_view()), name="tracklist")
]
