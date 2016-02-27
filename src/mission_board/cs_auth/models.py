from django.contrib.auth.models import User
from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=128)
    token = models.CharField(max_length=128)
    university = models.CharField(max_length=128)
    flag = models.CharField(max_length=128)
    color = models.CharField(max_length=128, default="#000000")
    score = models.IntegerField()
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # TODO check if these fields are relevent (with fields already in User)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    display_name = models.CharField(max_length=128)
    team = models.ForeignKey(Team)
    curriculum_vitae = models.FileField(blank=True, max_length=20000)
    score = models.IntegerField(default=0)

    def __str__(self):
        return "%s, %s %s, %s" % (self.display_name,
                                  self.first_name,
                                  self.last_name,
                                  self.team)

    def rank_level(self):
        if self.score < 10:
            return 1
        elif self.score < 25:
            return 2
        elif self.score < 50:
            return 3
        elif self.score < 100:
            return 4
        elif self.score < 250:
            return 5
        elif self.score < 500:
            return 6
        elif self.score < 1000:
            return 7
        elif self.score < 2500:
            return 8
        elif self.score < 5000:
            return 9
        elif self.score < 10000:
            return 10
        else:
            return 11
