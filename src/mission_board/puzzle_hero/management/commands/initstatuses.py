from django.core.management.base import BaseCommand, CommandError

from puzzle_hero.models import Track, Mission, Post, TrackStatus, \
        MissionStatus, PostStatus, Team


class Command(BaseCommand):
    help = "Initialize create a status for each track for each team."

    def handle(self, *args, **options):

        TrackStatus.objects.all().delete()
        MissionStatus.objects.all().delete()
        PostStatus.objects.all().delete()

        for team in Team.objects.all():
            print("Processing team: %s" % team.name)
            for track in Track.objects.all():
                print("\tProcessing track: %s" % track.title)
                track_stat = TrackStatus()
                track_stat.track = track
                track_stat.team = team
                track_stat.status = track.initial_status
                track_stat.save()

            for mission in Mission.objects.all():
                print("\tProcessing mission: %s" % mission.title)
                miss_stat = MissionStatus()
                miss_stat.mission = mission
                miss_stat.team = team
                miss_stat.status = mission.initial_status
                miss_stat.save()

            for post in Post.objects.all():
                print("\tProcessing post: %s" % post.id)
                post_stat = PostStatus()
                post_stat.post = post
                post_stat.team = team
                post_stat.status = post.initial_status
                post_stat.save()
