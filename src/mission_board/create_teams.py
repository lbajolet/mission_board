import os, django
import string
import random
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mission_board.settings")
django.setup()

from cs_auth.models import Team

# clear database
Team.objects.all().delete()

with open('data/teams.json') as json_data:
	json_teams = json.load(json_data)

	for json_team in json_teams:
		team = Team()
		team.name = json_team["name"]
		team.university = json_team["university"]
		team.token = json_team["token"]
		team.score = json_team["score"]
		team.save()

teams = Team.objects.all()
print("Loaded {} teams:".format(teams.count()))
for team in Team.objects.all():
	print("   * " + team.name)
