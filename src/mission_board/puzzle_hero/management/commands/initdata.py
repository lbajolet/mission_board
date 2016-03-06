import os
import shutil

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from cs_auth.models import Team, Player


class Command(BaseCommand):
    help = "Initialize data for the CSGames launch"

    def handle(self, *args, **options):
        call_command("migrate")
        call_command("loadteams")
        call_command("createtracks")
        self.createsuperuser()
        call_command("initstatuses")

    @staticmethod
    def createsuperuser():
        team = Team()
        team.name = "CSGO_Admin"
        team.university = "UQAM"
        team.token = "store170"
        team.score = 0
        team.hidden = True
        team.save()

        user = User()
        user.email = "info@csgames.org"
        user.username = "admin"
        user.first_name = "Romain"
        user.last_name = "Chanoir"
        user.is_staff = True
        user.is_superuser = True
        user.set_password("givehimthecorporationyo")
        user.save()

        player = Player()
        user.player = player
        player.last_name = "Romain"
        player.first_name = "Chanoir"
        player.display_name = "Bl4ckMinou"
        player.team = team

        player.save()
