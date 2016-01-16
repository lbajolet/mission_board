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
    mission = models.ForeignKey(Mission)
    team = models.ForeignKey(Team)


class PostStatus(models.Model):
    status = models.CharField(max_length=64)
    message = models.ForeignKey(Post)
    team = models.ForeignKey(Team)


class Submission(models.Model):
    submitter = models.ForeignKey(Player, blank=True)
    team = models.ForeignKey(Team)
    flag = models.ForeignKey(Flag)


class TrackStatusTrigger(models.Model):
    flag = models.ForeignKey(Flag)
    track = models.ForeignKey(Track)
    status = models.CharField(max_length=64)


class MissionStatusTrigger(models.Model):
    flag = models.ForeignKey(Flag)
    mission = models.ForeignKey(Mission)
    status = models.CharField(max_length=64)


class PostStatusTrigger(models.Model):
    flag = models.ForeignKey(Flag)
    post = models.ForeignKey(Post)
    status = models.CharField(max_length=64)

class TeamScoreTrigger(models.Model):
    flag = models.ForeignKey(Flag)
    score = models.IntegerField()

# Other possible triggers
# - Airdrop == score bonus? or what?
# - Announcement
# - Lock (say we want only one team to be able to solve a challenge...
#         lock it back for other teams)
# - ... More ideas?
