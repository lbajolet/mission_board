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

            delta = end - start
            for idx, flag in enumerate(flag_set):
                submit_delta = delta / (len(flag_set) + 1) * (idx + 1)
                submit_time = start + submit_delta

                player = Player.objects.filter(team=team).first()
                process_flag_submission(flag, player=player,
                                        datetime=submit_time)

