from django.db import models

from cs_auth.models import Team, Player


class Flag(models.Model):
    token = models.CharField(max_length=255)


class Track(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    initial_status = models.CharField(max_length=64)
    title = models.CharField(max_length=255)


class Mission(models.Model):
    track = models.ForeignKey(Track)
    id = models.CharField(max_length=64, primary_key=True)
    initial_status = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    reward = models.IntegerField()
    dependencies = models.ManyToManyField("self")


class Post(models.Model):
    mission = models.ForeignKey(Mission)
    id = models.CharField(max_length=64, primary_key=True)
    initial_status = models.CharField(max_length=64)
    sender = models.CharField(max_length=255)
    en = models.CharField(max_length=255)
    md_en = models.TextField()
    fr = models.CharField(max_length=255)
    md_fr = models.TextField()
    required_for = models.ForeignKey("self", related_name="depends_on", null=True)


class TrackStatus(models.Model):
    status = models.CharField(max_length=64)
    track = models.ForeignKey(Track, related_name='status')
    team = models.ForeignKey(Team)


class MissionStatus(models.Model):
    status = models.CharField(max_length=64)
    Mission = models.ForeignKey(Mission)
    Team = models.ForeignKey(Team)


class PostStatus(models.Model):
    status = models.CharField(max_length=64)
    message = models.ForeignKey(Post)
    Team = models.ForeignKey(Team)


class Submission(models.Model):
    submitter = models.ForeignKey(Player, blank=True)
    team = models.ForeignKey(Team)
    flag = models.ForeignKey(Flag)


class Trigger(models.Model):

    UNLOCK_TRACK = 0
    UNLOCK_MISSION = 1
    UNLOCK_POST = 2

    TYPE_CHOICES = (
        (UNLOCK_TRACK, 'unlock_track'),
        (UNLOCK_MISSION, 'unlock_mission'),
        (UNLOCK_POST, 'unlock_post'),
    )

    type = models.CharField(max_length=64, choices=TYPE_CHOICES)
    flag = models.ForeignKey(Flag)


class UnlockTrackTrigger(models.Model):
    trigger = models.ForeignKey(Trigger)
    track = models.ForeignKey(Track)


class UnlockMissionTrigger(models.Model):
    trigger = models.ForeignKey(Trigger)
    mission = models.ForeignKey(Mission)


class UnlockPostTrigger(models.Model):
    trigger = models.ForeignKey(Trigger)
    post = models.ForeignKey(Post)


# Other possible triggers
# - Airdrop
# - Announcement
# - Lock (say we want only one team to be able to solve a challenge...
#         lock it back for other teams)
# - ... More ideas?
