import os, django
import string
import random
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mission_board.settings")
django.setup()

from puzzle_hero.models import Track, Mission, Post
from puzzle_hero.models import Flag, TrackStatusTrigger, MissionStatusTrigger, PostStatusTrigger
from puzzle_hero.models import TeamScoreTrigger

# clear database
Track.objects.all().delete()
Mission.objects.all().delete()
Post.objects.all().delete()
Flag.objects.all().delete()
TrackStatusTrigger.objects.all().delete()
MissionStatusTrigger.objects.all().delete()
PostStatusTrigger.objects.all().delete()
TeamScoreTrigger.objects.all().delete()

# load track list
with open('data/tracks/tracks.json') as json_data:
    json_tracks = json.load(json_data)

# create and save db instances
for track_file in json_tracks:

    # create track data
    with open('data/tracks/' + track_file + '/track.json') as track_data:
        json_track = json.load(track_data)

        track = Track()
        track.id = json_track["id"]
        track.title = json_track["title"]
        track.initial_status = json_track["initial_status"]
        track.save()

        for json_mission in json_track["missions"]:
            mission = Mission()
            mission.track = track
            mission.id = json_mission["id"]
            mission.title = json_mission["title"]
            mission.reward = json_mission["reward"]
            mission.initial_status = json_mission["initial_status"]
            for dep in json_mission["dependencies"]:
                mission.dependencies.add(Mission.objects.get(id=dep))
            mission.save()

            for json_post in json_mission["posts"]:
                post = Post()
                post.mission = mission
                post.id = json_post["id"]
                post.initial_status = json_post["initial_status"]
                post.sender = json_post["sender"]

                post.en = json_post["en"]
                with open('data/tracks/' + track_file + '/' + post.en) as fr:
                    post.md_en = fr.read()

                post.fr = json_post["fr"]
                with open('data/tracks/' + track_file + '/' + post.fr) as fr:
                    post.md_fr = fr.read()

                post.save()

    # create flags and triggers data
    with open('data/tracks/' + track_file + '/flags.json') as flags_data:
        json_flags = json.load(flags_data)

        for json_flag in json_flags:
            flag = Flag()
            flag.flag = json_flag["flag"]
            flag.save()

            for json_trigger in json_flag["triggers"]:
                kind = json_trigger["kind"]

                if kind == "track_status":
                    trigger = TrackStatusTrigger()
                    trigger.flag = flag
                    trigger.track = Track.objects.get(id=json_trigger["track"])
                    trigger.status = json_trigger["status"]
                    trigger.save()
                elif kind == "mission_status":
                    trigger = MissionStatusTrigger()
                    trigger.flag = flag
                    trigger.mission = Mission.objects.get(id=json_trigger["mission"])
                    trigger.status = json_trigger["status"]
                    trigger.save()
                elif kind == "post_status":
                    trigger = PostStatusTrigger()
                    trigger.flag = flag
                    trigger.post = Post.objects.get(id=json_trigger["post"])
                    trigger.status = json_trigger["status"]
                    trigger.save()
                elif kind == "team_score":
                    trigger = TeamScoreTrigger()
                    trigger.flag = flag
                    trigger.score = json_trigger["reward"]
                    trigger.save()

tracks = Track.objects.all()
print("Loaded {} tracks:".format(tracks.count()))
for track in Track.objects.all():
    print(" # " + track.title)
    for mission in Mission.objects.filter(track=track):
        print("   * " + mission.title)
        for post in Post.objects.filter(mission=mission):
            print("       " + post.id)

flags = Flag.objects.all()
print("Loaded {} flags.".format(flags.count()))
for track in Track.objects.all():
    for mission in Mission.objects.filter(track=track):
        for post in Post.objects.filter(mission=mission):
            # check if all posts can be unlocked
            if post.initial_status == "open": continue
            triggers = PostStatusTrigger.objects.filter(post=post, status="open")
            if not triggers:
               print("WARNING: post {} can't be unlocked!".format(post.id))
        # check if all missions can be unlocked
        if mission.initial_status == "locked" and mission.dependencies.count() == 0:
            triggers = MissionStatusTrigger.objects.filter(mission=mission, status="open")
            if not triggers:
                print("WARNING: mission {} can't be unlocked!".format(mission.id))
        triggers = MissionStatusTrigger.objects.filter(mission=mission, status="closed")
        if not triggers:
            print("WARNING: mission {} can't be closed!".format(mission.id))

    # check if all tracks can be unlocked
    if track.initial_status == "open": continue
    triggers = TrackStatusTrigger.objects.filter(track=track)
    if not triggers:
        print("WARNING: track {} can't be unlocked!".format(track.id))
