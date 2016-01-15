from django.shortcuts import render
from django.views.generic import ListView

from .models import Track
from .models import Mission

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
