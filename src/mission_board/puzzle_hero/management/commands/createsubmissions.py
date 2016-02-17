import random
import datetime

from django.core.management import BaseCommand
from django.conf import settings
from django.utils import timezone

from cs_auth.models import Team, Player
from puzzle_hero.models import Flag, GlobalStatus, Submission
from puzzle_hero.triggers import process_flag_submission


class Command(BaseCommand):
    help = "Submit a few flags per team to populate the scoreboard."

    def handle(self, *args, **options):
        pass

        subs = Submission.objects.all()
        subs.delete()

        flags = Flag.objects.all()
        gs = GlobalStatus.objects.all().first()
        if not gs:
            gs = GlobalStatus()
        gs.start_time = timezone.now() - datetime.timedelta(2)
        gs.status = "started"
        gs.save()

        for team in Team.objects.all():

            flag_set = set()
            for i in range(random.randrange(len(flags))):
                rand_num = random.randrange(0, len(flags))
                flag_set.add(flags[rand_num])

            start = gs.start_time
            end = timezone.now()
            fake_now = start
            for flag in flag_set:

                delta = end - fake_now
                int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
                random_second = random.randrange(int_delta)
                rand_time = fake_now + datetime.timedelta(seconds=random_second)
                fake_now = rand_time

                player = Player.objects.filter(team=team).first()
                process_flag_submission(flag, player=player,
                                        datetime=rand_time)
