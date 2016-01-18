from django.db import models

from cs_auth.models import Team, Player


class Flag(models.Model):
    token = models.CharField(max_length=255)


class Track(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    initial_status = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    dependencies = models.ManyToManyField("self", related_name="required_for",
                                          blank=True, symmetrical=False)


class Mission(models.Model):
    track = models.ForeignKey(Track)
    id = models.CharField(max_length=64, primary_key=True)
    initial_status = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    reward = models.IntegerField()
    dependencies = models.ManyToManyField("self", related_name="required_for",
                                          blank=True, symmetrical=False)


class Post(models.Model):
    mission = models.ForeignKey(Mission)
    id = models.CharField(max_length=64, primary_key=True)
    initial_status = models.CharField(max_length=64)
    sender = models.CharField(max_length=255)
    en = models.CharField(max_length=255)
    md_en = models.TextField()
    fr = models.CharField(max_length=255)
    md_fr = models.TextField()


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
    post = models.ForeignKey(Post)
    team = models.ForeignKey(Team)


class Submission(models.Model):
    submitter = models.ForeignKey(Player, blank=True)
    team = models.ForeignKey(Team)
    flag = models.ForeignKey(Flag)


class Trigger(models.Model):

    TRACKSTATUS_TYPE = 1
    MISSIONSTATUS_TYPE = 2
    POSTSTATUS_TYPE = 3
    TEAMSCORE_TYPE = 4
    TYPE_CHOICES = (
        (TRACKSTATUS_TYPE, 'trackstatus'),
        (MISSIONSTATUS_TYPE, 'missionstatus'),
        (POSTSTATUS_TYPE, 'poststatus'),
        (TEAMSCORE_TYPE, 'teamscore'),
    )

    flag = models.ForeignKey(Flag)
    kind = models.IntegerField(choices=TYPE_CHOICES)


class TrackStatusTrigger(models.Model):
    trigger = models.OneToOneField(Trigger)
    track = models.ForeignKey(Track)
    status = models.CharField(max_length=64)


class MissionStatusTrigger(models.Model):
    trigger = models.OneToOneField(Trigger)
    mission = models.ForeignKey(Mission)
    status = models.CharField(max_length=64)


class PostStatusTrigger(models.Model):
    trigger = models.OneToOneField(Trigger)
    post = models.ForeignKey(Post)
    status = models.CharField(max_length=64)


class TeamScoreTrigger(models.Model):
    trigger = models.OneToOneField(Trigger)
    score = models.IntegerField()

# Other possible triggers
# - Airdrop == score bonus? or what?
# - Announcement
# - Lock (say we want only one team to be able to solve a challenge...
#         lock it back for other teams)
# - ... More ideas?
