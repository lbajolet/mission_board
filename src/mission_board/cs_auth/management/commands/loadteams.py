import csv

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from cs_auth.models import Player, Team
from puzzle_hero.models import Track, Mission, Post, TrackStatus, \
        MissionStatus, PostStatus


color_palette = ["#67DB96",
                 "#D14DE0",
                 "#DF4A2A",
                 "#6C9BD1",
                 "#D0D73A",
                 "#82724C",
                 "#DB3878",
                 "#DFA035",
                 "#7AE42C",
                 "#CB88DA",
                 "#52A335",
                 "#54927D",
                 "#D5C97B",
                 "#C0D5DC",
                 "#66DFCE",
                 "#A67076",
                 "#8A69E3",
                 "#D8AED0",
                 "#D5926D",
                 "#93872F",
                 "#C1E2B0",
                 "#4B7631",
                 "#677A87",
                 "#C36595",
                 "#D744B0",
                 "#5F7FDB",
                 "#C9B6A0",
                 "#D0555D",
                 "#B76130",
                 "#766B9F",
                 "#B3D866",
                 "#63B9D0",
                 "#6BE261",
                 "#9654AF",
                 "#71A164"]


class Command(BaseCommand):
    help = "Initialize create a status for each track for each team."

    def handle(self, *args, **options):

        # clear database
        Team.objects.all().delete()
        User.objects.all().delete()
        Player.objects.all().delete()

        with open('../../data/teams.csv') as csvfile:
            teams = csv.DictReader(csvfile)

            # import ipdb; ipdb.set_trace()

            for idx, (team_data, color) in enumerate(zip(teams, color_palette)):
                if team_data["Team Name"] == "":
                    continue

                team = Team()
                team.name = team_data["Team Name"]
                team.university = team_data["University"]
                team.token = team_data["Token"]
                team.color = color
                team.flag = "flag%s" % idx
                team.score = 0
                team.save()


        teams = Team.objects.all()
        print("Loaded {} teams:".format(teams.count()))
        for team in teams:
            print(team)
