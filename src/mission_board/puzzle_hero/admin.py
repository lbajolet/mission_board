from django.contrib import admin

from .models import Track, Mission, Post, TrackStatus, MissionStatus, \
    PostStatus, Submission, GlobalAnnouncement, TeamAnnouncement, \
    TrackAnnouncement, MissionAnnouncement, PostAnnouncement, Event, \
    PlayerEvent


class TrackAdmin(admin.ModelAdmin):
    pass


class MissionAdmin(admin.ModelAdmin):
    ordering = ("track", "title")


class PostAdmin(admin.ModelAdmin):
    ordering = ("mission__track", "mission", "id")


class TrackStatusAdmin(admin.ModelAdmin):
    ordering = ("team__name", "track__title")


class MissionStatusAdmin(admin.ModelAdmin):
    ordering = ("team__name", "mission__title")
    list_display = ('team', 'mission', 'status')


class PostStatusAdmin(admin.ModelAdmin):
    ordering = ("team__name", "post__mission__title", "id")


class SubmissionAdmin(admin.ModelAdmin):
    pass


class GlobalAnnouncementAdmin(admin.ModelAdmin):
    pass


class TeamAnnouncementAdmin(admin.ModelAdmin):
    pass


class TrackAnnouncementAdmin(admin.ModelAdmin):
    pass


class MissionAnnouncementAdmin(admin.ModelAdmin):
    pass


class PostAnnouncementAdmin(admin.ModelAdmin):
    pass


class EventAdmin(admin.ModelAdmin):
    pass


class PlayerEventAdmin(admin.ModelAdmin):
    pass


admin.site.register(Track, TrackAdmin)
admin.site.register(Mission, MissionAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(TrackStatus, TrackStatusAdmin)
admin.site.register(MissionStatus, MissionStatusAdmin)
admin.site.register(PostStatus, PostStatusAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(GlobalAnnouncement, GlobalAnnouncementAdmin)
admin.site.register(TeamAnnouncement, TeamAnnouncementAdmin)
admin.site.register(TrackAnnouncement, TrackAnnouncementAdmin)
admin.site.register(MissionAnnouncement, MissionAnnouncementAdmin)
admin.site.register(PostAnnouncement, PostAnnouncementAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(PlayerEvent, PlayerEventAdmin)
