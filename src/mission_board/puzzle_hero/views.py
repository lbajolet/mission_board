from django.shortcuts import render
from django.views.generic import ListView

from .models import TrackStatus


# Create your views here.
def index(request):
    return render(request, "base.html")


class MissionBoardHome(ListView):
    model = TrackStatus
    context_object_name = 'trackstatus'
    template_name = 'puzzle_hero/mission_board_home.html'

    def get_queryset(self):
        return TrackStatus.objects.filter(
            team=self.request.user.player.team
        )


