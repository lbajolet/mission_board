from django.contrib.auth.models import User
from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=128)
    token = models.CharField(max_length=128)
    university = models.CharField(max_length=128)
    score = models.IntegerField()


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    display_name = models.CharField(max_length=128)
    team = models.ForeignKey(Team)
