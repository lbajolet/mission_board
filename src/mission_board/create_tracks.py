import os, django
import string
import random
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mission_board.settings")
django.setup()

from puzzle_hero.models import Track, Mission, Post

# clear database
Track.objects.all().delete()
Mission.objects.all().delete()
Post.objects.all().delete()

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

tracks = Track.objects.all()
print("Loaded {} tracks:".format(tracks.count()))
for track in Track.objects.all():
    print(" # " + track.title)
    for mission in Mission.objects.filter(track=track):
        print("   * " + mission.title)
        for post in Post.objects.filter(mission=mission):
            print("       " + post.id)
