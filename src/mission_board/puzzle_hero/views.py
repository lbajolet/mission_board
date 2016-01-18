from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView

from cs_auth.models import Team

from .forms import FlagSubmissionForm
from .models import Mission, MissionStatus, Post, PostStatus, Track, \
    TrackStatus, Submission, Flag
from .triggers import process_flag_submission

import json
import markdown


class MissionBoardHome(ListView):
    model = Track
    context_object_name = 'tracks'
    template_name = 'puzzle_hero/mission_board_home.html'

    def get_queryset(self):
        tracks = Track.objects.all()
        for track in tracks:
            track.missions = Mission.objects.filter(track=track)
        return tracks

    def get_context_data(self, **kwargs):
        context = super(MissionBoardHome, self).get_context_data(**kwargs)
        context['flag_form'] = FlagSubmissionForm()

        team = self.request.user.player.team
        track_statuses = TrackStatus.objects.filter(team=team)
        mission_statuses = MissionStatus.objects.filter(team=team)
        context["track_statuses"] = track_statuses
        context["mission_statuses"] = mission_statuses

        return context


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

    def get_context_data(self, **kwargs):
        context = super(MissionBoardMission, self).get_context_data(**kwargs)
        context['flag_form'] = FlagSubmissionForm()
        return context


class MissionBoardTeams(ListView):
    model = Team
    context_object_name = 'teams'
    template_name = 'puzzle_hero/mission_board_teams.html'

    def get_queryset(self):
        return Team.objects.all().order_by("score")


def team_stats(request):
    team = request.user.player.team

    track_stati = TrackStatus.objects.filter(team=team)
    completed_tracks = [ts.track for ts in track_stati]

    mission_stati = MissionStatus.objects.filter(team=team)
    completed_missions = [ms.mission for ms in mission_stati]

    post_stati = PostStatus.objects.filter(team=team)
    completed_posts = [ps.post for ps in post_stati]

    context = {
        "tracks": completed_tracks,
        "missions": completed_missions,
        "posts": completed_posts
    }

    return render(request, "puzzle_hero/team_stats.html", context)


def submit_flag(request):
    if request.method == 'POST':
        player = request.user.player
        form = FlagSubmissionForm(request.POST)
        if form.is_valid():
            # Check if flag has already been submitted:
            flag_token = form.cleaned_data["token"]
            flag = Flag.objects.filter(token=flag_token).first()

            subs = Submission.objects.filter(flag=flag,
                                             team=player.team)

            # Flag has already been submitted by this team
            if subs:
                messages.add_message(
                    request,
                    messages.WARNING,
                    "This flag has already been submitted."
                )
                return HttpResponseRedirect(request.META['HTTP_REFERER'])

            else:
                process_flag_submission(flag, player)
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Submitted flag %s!' % form.cleaned_data["token"]
                )
                return HttpResponseRedirect(request.META['HTTP_REFERER'])

        else:
            wrong_flag = form.data["token"]
            messages.add_message(request, messages.ERROR,
                                 'Invalid flag %s !' % wrong_flag)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
