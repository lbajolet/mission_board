from django.db import models

from cs_auth.models import Team, Player


class Track(models.Model):
    pass


class Challenge(models.Model):
    track = models.ForeignKey(Track)
    required_for = models.ForeignKey("self", related_name="depends_on", null=True)


class Post(models.Model):
    challenge = models.ForeignKey(Challenge)
    required_for = models.ForeignKey("self", related_name="depends_on", null=True)


class TrackStatus(models.Model):
    status = models.CharField(max_length=64)
    track = models.ForeignKey(Track)
    Team = models.ForeignKey(Team)


class ChallengeStatus(models.Model):
    status = models.CharField(max_length=64)
    challenge = models.ForeignKey(Challenge)
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
