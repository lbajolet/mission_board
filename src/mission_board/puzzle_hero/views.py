from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import ListView, FormView

from cs_auth.models import Team

from .forms import FlagSubmissionForm, GlobalAnnouncementForm
from .models import Mission, MissionStatus, Post, PostStatus, Track, \
    TrackStatus, Submission, Flag
from .triggers import process_flag_submission

import json
import markdown


# Used as test function to in several auths on views
def user_is_player(user):
    return hasattr(user, "player")


def user_is_csadmin(user):
    return user.is_superuser


class TracksList(LoginRequiredMixin, ListView):
    model = Track
    context_object_name = 'tracks'
    template_name = 'puzzle_hero/tracks_list.html'

    def get_queryset(self):
        tracks = Track.objects.all()
        for track in tracks:
            track.missions = Mission.objects.filter(track=track)
        return tracks

    def get_context_data(self, **kwargs):
        context = super(TracksList, self).get_context_data(**kwargs)
        context['flag_form'] = FlagSubmissionForm()

        team = self.request.user.player.team
        track_statuses = TrackStatus.objects.filter(team=team)
        mission_statuses = MissionStatus.objects.filter(team=team)
        context["track_statuses"] = track_statuses
        context["mission_statuses"] = mission_statuses

        context["nav"] = "missions"

        return context


class MissionPage(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Mission
    context_object_name = 'mission'
    template_name = 'puzzle_hero/mission_page.html'

    def test_func(self):
        return user_is_player(self.request.user)

    def get_queryset(self):
        mission = Mission.objects.filter(id=self.kwargs.get('mission'))[0]
        mission.posts = Post.objects.filter(mission=mission)
        for post in mission.posts:
            post.html_en = markdown.markdown(post.md_en)
            post.html_fr = markdown.markdown(post.md_fr)

        return mission

    def get_context_data(self, **kwargs):
        context = super(MissionPage, self).get_context_data(**kwargs)
        context['flag_form'] = FlagSubmissionForm()
        return context


class Scoreboard(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Team
    context_object_name = 'teams'
    template_name = 'puzzle_hero/scoreboard.html'

    def test_func(self):
        return user_is_player(self.request.user)

    def get_queryset(self):
        return Team.objects.all().order_by("score")

    def get_context_data(self, **kwargs):
        context = super(Scoreboard, self).get_context_data(**kwargs)
        context["nav"] = "scoreboard"
        return context


@login_required
@user_passes_test(user_is_player)
def team_stats(request, team_id):
    team = Team.objects.filter(id=team_id)[0]

    track_statuses = TrackStatus.objects.filter(team=team)
    completed_tracks = [ts.track for ts in track_statuses]

    mission_statuses = MissionStatus.objects.filter(team=team)
    completed_missions = [ms.mission for ms in mission_statuses]

    post_statuses = PostStatus.objects.filter(team=team)
    completed_posts = [ps.post for ps in post_statuses]

    context = {
        "tracks": completed_tracks,
        "missions": completed_missions,
        "posts": completed_posts
    }

    return render(request, "puzzle_hero/team_stats.html", context)


@login_required
@user_passes_test(user_is_player)
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
                process_flag_submission(flag, request)
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


@login_required
@user_passes_test(user_is_csadmin)
def csadmin_index(request):
    return redirect("admin:index")


class CSAdminGlobalAnnouncementView(FormView):
    form_class = GlobalAnnouncementForm
    template_name = "cs_auth/login.html"
