from django.db import models
from django.utils import timezone

from cs_auth.models import Team, Player


class Flag(models.Model):
    token = models.CharField(max_length=255)


class Track(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    initial_status = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    dependencies = models.ManyToManyField("self", related_name="required_for",
                                          blank=True, symmetrical=False)
    disabled = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Mission(models.Model):
    track = models.ForeignKey(Track)
    id = models.CharField(max_length=64, primary_key=True)
    initial_status = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    reward = models.IntegerField()
    dependencies = models.ManyToManyField("self", related_name="required_for",
                                          blank=True, symmetrical=False)
    disabled = models.BooleanField(default=False)

    def __str__(self):
        return "%s: %s" % (self.track, self.title)


class Post(models.Model):
    mission = models.ForeignKey(Mission)
    id = models.CharField(max_length=64, primary_key=True)
    initial_status = models.CharField(max_length=64)
    sender = models.CharField(max_length=255)
    en = models.CharField(max_length=255)
    md_en = models.TextField()
    fr = models.CharField(max_length=255)
    md_fr = models.TextField()

    def __str__(self):
        return "%s: %s : %s" % (self.mission.track, self.mission, self.id)


# TODO Enum status choices
class TrackStatus(models.Model):
    status = models.CharField(max_length=64)
    track = models.ForeignKey(Track, related_name='status')
    team = models.ForeignKey(Team)

    def __str__(self):
        return "%s :: %s" % (self.team.name, self.track.title)

    class Meta:
        verbose_name_plural = "Track Statuses"


class MissionStatus(models.Model):
    status = models.CharField(max_length=64)
    mission = models.ForeignKey(Mission)
    team = models.ForeignKey(Team)

    def __str__(self):
        return "%s :: %s :: %s" % (self.team.name, self.mission.track.title,
                                   self.mission.title)

    class Meta:
        verbose_name_plural = "Mission Statuses"


class PostStatus(models.Model):
    status = models.CharField(max_length=64)
    post = models.ForeignKey(Post)
    team = models.ForeignKey(Team)

    def __str__(self):
        return "%s :: %s :: %s - %s" % (self.team.name,
                                        self.post.mission.track.title,
                                        self.post.mission.title,
                                        self.id)

    class Meta:
        verbose_name_plural = "Post Statuses"


# TODO add a bad submission model
class Submission(models.Model):
    submitter = models.ForeignKey(Player, blank=True)
    team = models.ForeignKey(Team)
    flag = models.ForeignKey(Flag)
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "[%s] %s: %s" % (self.time.strftime("%Y/%m/%d - %H:%M"),
                                self.team.name,
                                self.flag.token)


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


class Announcement(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    class Meta:
        abstract = True


class GlobalAnnouncement(Announcement):
    def __str__(self):
        if len(self.message) >= 20:
            to_s_msg = self.message[:20]
        else:
            to_s_msg = self.message

        return "[%s] %s" % (self.time.strftime("%Y/%m/%d - %H:%M"),
                            to_s_msg)


class TeamAnnouncement(Announcement):
    team = models.ForeignKey(Team)

    def __str__(self):
        if len(self.message) >= 20:
            to_s_msg = self.message[:20] + "..."
        else:
            to_s_msg = self.message

        return "[%s] %s: %s" % (self.time.strftime("%Y/%m/%d - %H:%M"),
                                self.team.name,
                                to_s_msg)


class TrackAnnouncement(Announcement):
    track = models.ForeignKey(Track)

    def __str__(self):
        if len(self.message) >= 20:
            to_s_msg = self.message[:20] + "..."
        else:
            to_s_msg = self.message
        return "[%s] %s: %s" % (self.time.strftime("%Y/%m/%d - %H:%M"),
                                self.track.title,
                                to_s_msg)


class MissionAnnouncement(Announcement):
    mission = models.ForeignKey(Mission)

    def __str__(self):
        if len(self.message) >= 20:
            to_s_msg = self.message[:20] + "..."
        else:
            to_s_msg = self.message

        return "[%s] %s: %s" % (self.time.strftime("%Y/%m/%d - %H:%M"),
                                self.mission.title,
                                to_s_msg)


class PostAnnouncement(Announcement):
    post = models.ForeignKey(Post)

    def __str__(self):
        if len(self.message) >= 20:
            to_s_msg = self.message[:20] + "..."
        else:
            to_s_msg = self.message
        return "[%s] %s: %s: %s: %s" % (self.time.strftime("%Y/%m/%d - %H:%M"),
                                        self.post.mission.track.title,
                                        self.post.mission.title,
                                        self.post.id,
                                        to_s_msg)


class Event(models.Model):
    player_event = models.BooleanField(default=False)
    type = models.CharField(max_length=128)
    message = models.TextField()
    time = models.DateTimeField(default=timezone.now)


class PlayerEvent(Event):
    player = models.ForeignKey(Player)


class ScoreEvent(Event):
    score_delta = models.IntegerField()
    score_total = models.IntegerField()
    team = models.ForeignKey(Team)


class GlobalStatus(models.Model):
    status = models.CharField(max_length=64)
    paused = models.BooleanField(default=False)
    start_time = models.DateTimeField()
