from django.contrib import admin

from .models import Track, Mission, Post, TrackStatus, MissionStatus, \
    PostStatus, Submission, GlobalAnnouncement, TeamAnnouncement, \
    TrackAnnouncement, MissionAnnouncement, PostAnnouncement, Event, \
    PlayerEvent, GlobalStatus, Flag, TeamScoreTrigger, BadFlagEvent


class TrackAdmin(admin.ModelAdmin):
    ordering = ("title", )
    list_display = ("title", "id", "disabled")


class MissionAdmin(admin.ModelAdmin):
    ordering = ("track", "title")
    list_display = ("track", "title", "reward", "id", "disabled")


class PostAdmin(admin.ModelAdmin):
    ordering = ("mission__track", "mission", "id")
    list_display = ("get_track", "mission", "id")

    def get_track(self, obj):
        return obj.mission.track
    get_track.short_description = "Track Name"
    get_track.admin_order_field = "mission__track__name"


class TrackStatusAdmin(admin.ModelAdmin):
    ordering = ("team__name", "track__title")
    list_display = ("track", "get_university", "team", "status")
    search_fields = ("track__title", "team__university", "team__name", "status")
    exclude = ("team", "track")

    def get_university(self, obj):
        return obj.team.university
    get_university.short_description = 'University'
    get_university.admin_order_field = 'team__university'


class MissionStatusAdmin(admin.ModelAdmin):
    ordering = ("team__name", "mission__title")
    list_display = ('team', 'get_university', 'get_track', 'mission', 'status')
    search_fields = ('status', 'team__name', 'mission__title',
                     'mission__track__title', 'team__university')
    exclude = ("team", "mission")

    def get_track(self, obj):
        return obj.mission.track.title
    get_track.short_description = 'Track'
    get_track.admin_order_field = 'mission__track__title'

    def get_university(self, obj):
        return obj.team.university
    get_university.short_description = 'University'
    get_university.admin_order_field = 'team__university'


class PostStatusAdmin(admin.ModelAdmin):
    ordering = ("post__id",)
    list_display = ("team", "get_university", "get_track", "get_mission",
                    "get_post", "status")
    search_fields = ("post__id", "team__name")
    exclude = ("post", "team")

    def get_university(self, obj):
        return obj.team.university
    get_university.short_description = 'University'
    get_university.admin_order_field = 'team__university'

    def get_post(self, obj):
        return obj.post.id
    get_post.short_description = "Post"
    get_post.admin_order_field = "post__id"

    def get_track(self, obj):
        return obj.post.mission.track
    get_track.short_description = "Track"
    get_track.admin_order_field = "post__mission__track__name"

    def get_mission(self, obj):
        return obj.post.mission
    get_mission.short_description = "Mission"
    get_mission.admin_order_field = "post__mission__name"


class SubmissionAdmin(admin.ModelAdmin):
    search_fields = ("flag__token", "team__name")
    list_display = ("get_flag", "team")

    def get_flag(self, obj):
        return obj.flag.token
    get_flag.short_description = "Flag"


class GlobalAnnouncementAdmin(admin.ModelAdmin):
    ordering = ("-time", )
    list_display = ("time", "message")
    search_fields = ("message",)


class TeamAnnouncementAdmin(admin.ModelAdmin):
    ordering = ("team", "-time")
    list_display = ("time", "team", "message")
    search_fields = ("team__name", "message")


class TrackAnnouncementAdmin(admin.ModelAdmin):
    ordering = ("track__title", "-time")
    list_display = ("time", "track", "message")
    search_fields = ("track__title", "message")


class MissionAnnouncementAdmin(admin.ModelAdmin):
    ordering = ("mission__track__title", "mission__title", "-time")
    list_display = ("time", "get_track", "mission", "message")
    search_fields = ("mission__title", "mission__track__title" "message")

    def get_track(self, obj):
        return obj.mission.track
    get_track.short_description = "Track"


class PostAnnouncementAdmin(admin.ModelAdmin):
    ordering = ("post__mission__track__title", "post__mission__title", "-time")
    list_display = ("time", "get_track", "get_mission", "post", "message")
    search_fields = ("post__id", "mission__title", "mission__track__title",
                     "message")

    def get_track(self, obj):
        return obj.post.mission.track
    get_track.short_description = "Track"

    def get_mission(self, obj):
        return obj.post.mission.title
    get_mission.short_description = "Mission"


class EventAdmin(admin.ModelAdmin):
    list_display = ("time", "type", "message")
    search_fields = ("time", "type", "message")


class PlayerEventAdmin(admin.ModelAdmin):
    list_display = ("time", "type", "player", "message")
    search_fields = ("time", "type", "player__display_name", "message")


class GlobalStatusAdmin(admin.ModelAdmin):
    pass


class FlagAdmin(admin.ModelAdmin):
    ordering = ("token", )
    list_display = ("token", "get_score")
    search_fields = ("token", )

    def get_score(self, obj):
        ts = TeamScoreTrigger.objects.filter(trigger__flag=obj).first()
        if ts:
            return ts.score
        else:
            return 0
    get_score.short_description = "Score"


class BadFlagEventAdmin(admin.ModelAdmin):
    ordering = ("-time", "player__team__name", "player",)
    list_display = ("time", "get_team", "get_university", "player", "token")
    search_fields = ("player__display_name", "player__team__name", "player__team__university",
                     "token")

    def get_team(self, obj):
        return obj.player.team
    get_team.short_description = "Team"
    get_team.admin_order_field = "player__team__name"

    def get_university(self, obj):
        return obj.player.team.university
    get_university.short_description = "University"
    get_university.admin_order_field = "player__team__university"

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
admin.site.register(GlobalStatus, GlobalStatusAdmin)
admin.site.register(Flag, FlagAdmin)
admin.site.register(BadFlagEvent, BadFlagEventAdmin)
