from django.contrib.auth.models import User
from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=128)
    token = models.CharField(max_length=128)
    university = models.CharField(max_length=128)
    score = models.IntegerField()

    def __str__(self):
        return "%s - %s" % (self.name, self.university)


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # TODO check if these fields are relevent (with fields already in User)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    display_name = models.CharField(max_length=128)
    team = models.ForeignKey(Team)

    def __str__(self):
        return "%s, %s %s, %s" % (self.display_name,
                                  self.first_name,
                                  self.last_name,
                                  self.team)
