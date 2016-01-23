import json

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from cs_auth.models import Player, Team
from puzzle_hero.models import Track, Mission, Post, TrackStatus, \
        MissionStatus, PostStatus


class Command(BaseCommand):
    help = "Initialize create a status for each track for each team."

    def handle(self, *args, **options):

        # clear database
        Team.objects.all().delete()
        User.objects.all().delete()
        Player.objects.all().delete()

        with open('../../data/teams.json') as json_data:
            json_teams = json.load(json_data)

            for json_team in json_teams:
                team = Team()
                team.name = json_team["name"]
                team.university = json_team["university"]
                team.token = json_team["token"]
                team.score = json_team["score"]
                team.save()

                univ_mail = json_team["university"].replace(" ", "") + ".com"

                user = User()
                user.email = "player@" + univ_mail
                user.username = "player_" + univ_mail[:-4].lower()
                user.first_name = "First-Name"
                user.last_name = "Last Name"
                user.set_password("12qwaszx")
                user.save()

                player = Player()
                user.player = player
                player.last_name = "Last Name"
                player.first_name = "First-Name"
                player.display_name = "Rebel_" + univ_mail
                player.team = team

                player.save()

        teams = Team.objects.all()
        print("Loaded {} teams:".format(teams.count()))
        for team in Team.objects.all():
            player = team.player_set.all().first()
            print("   * " + team.name, "Player login:", player.user.username, "12qwaszx")
