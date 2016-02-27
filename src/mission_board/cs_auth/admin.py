from django.contrib import admin

from .models import Team, Player


class TeamAdmin(admin.ModelAdmin):
    ordering = ("university", "name")
    list_display = ("name", "university", "score")
    search_fields = ("name", "university")


class PlayerAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "first_name", "last_name", "team",
                    "get_university", "score")
    search_fields = ("display_name", "first_name", "last_name", "team__name",
                     "team__university", "score")
    exclude = ("team", )

    def get_university(self, obj):
        return obj.team.university
    get_university.short_description = "University"
    get_university.admin_order_field = "team__university"

admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
