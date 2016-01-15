from django.db import models

from cs_auth.models import Team, Player


class Track(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    title = models.CharField(max_length=255)


class Mission(models.Model):
    track = models.ForeignKey(Track)
    id = models.CharField(max_length=64, primary_key=True)
    title = models.CharField(max_length=255)
    reward = models.IntegerField()
    dependencies = models.ManyToManyField("self")


class Post(models.Model):
    mission = models.ForeignKey(Mission)
    id = models.CharField(max_length=64, primary_key=True)
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


class Flag(models.Model):
    pass


class Submission(models.Model):
    submitter = models.ForeignKey(Player, blank=True)
    team = models.ForeignKey(Team)
    flag = models.ForeignKey(Flag)


class Trigger(models.Model):
    flag = models.ForeignKey(Flag)
    type = models.CharField(max_length=64)
