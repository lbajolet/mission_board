from django.shortcuts import render
from django.views.generic import ListView

from cs_auth.models import Team
from .models import Track
from .models import Mission
from .models import Post

import json
import markdown

# Create your views here.
def index(request):
	return render(request, "base.html")


class MissionBoardHome(ListView):
	model = Track
	context_object_name = 'tracks'
	template_name = 'puzzle_hero/mission_board_home.html'

	def get_queryset(self):
		tracks = Track.objects.all()
		for track in tracks:
			track.missions = Mission.objects.filter(track=track)
		return tracks

class MissionBoardMission(ListView):
	model = Mission
	context_object_name = 'mission'
	template_name = 'puzzle_hero/mission_board_mission.html'

	def get_queryset(self):
		mission = Mission.objects.filter(id=self.kwargs.get('mission'))[0]
		mission.posts = Post.objects.filter(mission=mission)
		for post in mission.posts:
			post.html_en = markdown.markdown(post.md_en)
			post.html_fr = markdown.markdown(post.md_fr)

		return mission

class MissionBoardTeams(ListView):
	model = Team
	context_object_name = 'teams'
	template_name = 'puzzle_hero/mission_board_teams.html'

	def get_queryset(self):
		return Team.objects.all()
