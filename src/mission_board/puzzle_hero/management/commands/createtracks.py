import json
import hashlib
import os
import re
import shutil
import sys

from django.core.management import BaseCommand
from django.conf import settings

from puzzle_hero.models import Track, Mission, Post
from puzzle_hero.models import Flag, Trigger, TrackStatusTrigger, \
                               MissionStatusTrigger, PostStatusTrigger, \
                               TeamScoreTrigger

global count
count = 0


class Command(BaseCommand):
    help = "Initialize create a status for each track for each team."

    def relocate_ressources(self, dirname, text):

        res_pattern = """\[[a-zA-Z0-9._ \/]+\]\(([a-zA-Z0-9._ \/]+)\)"""
        r = re.compile(res_pattern)
        matches = re.findall(r, text)

        if matches:
            for match in matches:
                src = os.path.join(dirname, match)
                dst = self.convert_path(match)

                self.copy_to_staticdir(src, dst)
                text = text.replace(match, os.path.join(settings.STATIC_URL,
                                                        dst))

        return text

    def convert_path(self, path):

        global count
        count += 1

        # this is "insecure" but it will do for the weekend =P
        to_hash = ("%s%s%s" % (count, path, "kek")).encode("ascii")
        hashed = hashlib.sha256(to_hash).hexdigest()

        new = os.path.join('resources', hashed, path)

        print("Relocated resource file:")
        print("  - From:", path)
        print("  - To:  ", new)

        return new

    def copy_to_staticdir(self, src, dst):

        if not os.path.isfile(src):
            print("File does not exist:", src)
            sys.exit(0)

        dst = os.path.join(settings.BASE_DIR, 'static', dst)
        if not os.path.isdir(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))

        shutil.copy2(src, dst)

    def handle(self, *args, **options):
        # clear database
        Track.objects.all().delete()
        Mission.objects.all().delete()
        Post.objects.all().delete()
        Flag.objects.all().delete()
        TrackStatusTrigger.objects.all().delete()
        MissionStatusTrigger.objects.all().delete()
        PostStatusTrigger.objects.all().delete()
        TeamScoreTrigger.objects.all().delete()

        res_dir = os.path.join(settings.BASE_DIR, 'static', 'resources')
        if os.path.isdir(res_dir):
            shutil.rmtree(res_dir)
            shutil.mkdirs(res_dir)

        # load track list
        with open('../../data/tracks/tracks.json') as json_data:
            json_tracks = json.load(json_data)

        mission_deps = {}

        # create and save db instances
        for track_file in json_tracks:

            # create track data
            with open('../../data/tracks/' + track_file + '/track.json') as track_data:
                print("Load track " + track_file)
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
                    mission.kind = json_mission["kind"]
                    mission.initial_status = json_mission["initial_status"]
                    mission.save()

                    m_deps = [dep for dep in json_mission["dependencies"]]
                    mission_deps[mission.id] = m_deps
                    # for dep in json_mission["dependencies"]:
                    #     mission.dependencies.add(Mission.objects.get(id=dep))

                    for json_post in json_mission["posts"]:
                        post = Post()
                        post.mission = mission
                        post.id = json_post["id"]
                        post.initial_status = json_post["initial_status"]
                        post.sender = json_post["sender"]

                        post.en = json_post["en"]
                        posts_dir = os.path.join('../../data/tracks/', track_file)
                        with open(os.path.join(posts_dir, post.en)) as fr:
                            post_text = fr.read()
                            post_dir = os.path.join(
                                posts_dir,
                                os.path.dirname(post.en)
                            )

                            post.md_en = self.relocate_ressources(post_dir,
                                                                  post_text)

                        post.fr = json_post["fr"]
                        with open(os.path.join(posts_dir, post.fr)) as fr:
                            post_text = fr.read()
                            post_dir = os.path.join(
                                posts_dir,
                                os.path.dirname(post.en)
                            )

                            post.md_fr = self.relocate_ressources(post_dir,
                                                                  post_text)

                        post.save()

        # Mission dependencies
        for miss in Mission.objects.all():
            for dep in mission_deps[miss.id]:
                miss.dependencies.add(Mission.objects.get(id=dep))
            miss.save()

        # create and save db instances
        for track_file in json_tracks:

            # create flags and triggers data
            with open('../../data/tracks/' + track_file + '/flags.json') as flags_data:
                json_flags = json.load(flags_data)

                for json_flag in json_flags:
                    flag = Flag()
                    flag.token = json_flag["flag"]
                    flag.save()

                    for json_trigger in json_flag["triggers"]:

                        parent_trig = Trigger()
                        parent_trig.flag = flag

                        kind = json_trigger["kind"]

                        if kind == "track_status":
                            parent_trig.kind = 1
                            parent_trig.save()

                            trigger = TrackStatusTrigger()
                            trigger.trigger = parent_trig
                            trigger.track = Track.objects.get(id=json_trigger["track"])
                            trigger.status = json_trigger["status"]
                            trigger.save()
                        elif kind == "mission_status":
                            parent_trig.kind = 2
                            parent_trig.save()

                            trigger = MissionStatusTrigger()
                            trigger.trigger = parent_trig
                            trigger.mission = Mission.objects.get(id=json_trigger["mission"])
                            trigger.status = json_trigger["status"]
                            trigger.save()
                        elif kind == "post_status":
                            parent_trig.kind = 3
                            parent_trig.save()

                            trigger = PostStatusTrigger()
                            trigger.trigger = parent_trig
                            trigger.post = Post.objects.get(id=json_trigger["post"])
                            trigger.status = json_trigger["status"]
                            trigger.save()
                        elif kind == "team_score":
                            parent_trig.kind = 4
                            parent_trig.save()

                            trigger = TeamScoreTrigger()
                            trigger.trigger = parent_trig
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
            if track.initial_status == "open":
                continue

            triggers = TrackStatusTrigger.objects.filter(track=track)
            if not triggers:
                print("WARNING: track {} can't be unlocked!".format(track.id))
