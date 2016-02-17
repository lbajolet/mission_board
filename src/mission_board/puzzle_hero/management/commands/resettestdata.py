import os
import shutil

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from cs_auth.models import Team, Player


class Command(BaseCommand):
    help = "Reinitialize testing db. Clear migrations. Reload test data."

    def handle(self, *args, **options):
        self.delete_db_file()
        self.delete_migrations()
        call_command("migrate")
        call_command("makemigrations")
        call_command("makemigrations", "cs_auth")
        call_command("makemigrations", "puzzle_hero")
        call_command("makemigrations")
        call_command("migrate")
        call_command("createteams")
        call_command("createtracks")
        self.createsuperuser()
        call_command("initstatuses")
        call_command("createsubmissions")

    @staticmethod
    def delete_db_file():
        try:
            db = settings.DATABASES["default"]["NAME"]
            print("Removing %s" % db)
            os.remove(db)
        except FileNotFoundError:
            print("DB file not found... passing.")

    @staticmethod
    def delete_migrations():
        try:
            shutil.rmtree("cs_auth/migrations")
        except FileNotFoundError:
            print("No cs_auth migrations... passing.")

        try:
            shutil.rmtree("puzzle_hero/migrations")
        except FileNotFoundError:
            print("No puzzle_hero migrations... passing.")

    @staticmethod
    def createsuperuser():
        team = Team()
        team.name = "CSGO_Admin"
        team.university = "UQUAM"
        team.token = "ADMINTOKEN"
        team.score = 42
        team.save()

        univ_mail = "uqam.qc.ca"

        user = User()
        user.email = "player@" + univ_mail
        user.username = "root"
        user.first_name = "The"
        user.last_name = "Spear"
        user.is_staff = True
        user.is_superuser = True
        user.set_password("12qwaszx")
        user.save()

        player = Player()
        user.player = player
        player.last_name = "Spear"
        player.first_name = "The"
        player.display_name = "Klammydia"
        player.team = team

        player.save()
