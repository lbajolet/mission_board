import json
import base64

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import ListView, FormView, DetailView

from cs_auth.models import Team

from .forms import FlagSubmissionForm, GlobalAnnouncementForm
from .models import Mission, MissionStatus, Post, PostStatus, Track, \
    TrackStatus, Submission, Flag, GlobalAnnouncement, TeamAnnouncement, \
    TrackAnnouncement, MissionAnnouncement, PostAnnouncement
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

        tree_data = self._build_tree_data(track_statuses, mission_statuses)
        context["tree_data"] = tree_data

        context["global_announcements"] = GlobalAnnouncement.objects.all()
        context["team_announcements"] = TeamAnnouncement.objects.filter(team=team)

        context["nav"] = "missions"

        return context

    @staticmethod
    def _build_tree_data(track_statuses, mission_statuses):
        data = {}
        for ts in track_statuses:
            if ts.status == "open" or ts.status == "closed":

                track_data = {}
                for ms in mission_statuses:

                    if ms.mission.track != ts.track:
                        continue

                    mission_data = {}
                    mission_data["title"] = ms.mission.title
                    mission_data["status"] = ms.status
                    mission_data["reward"] = ms.mission.reward

                    dep_data = []
                    for dep in ms.mission.dependencies.all():
                        dep_data.append(dep.id)
                    if len(dep_data) > 0:
                        mission_data["dependencies"] = dep_data

                    track_data[ms.mission.id] = mission_data

                track_data = base64.b64encode(
                    json.dumps(track_data).encode("ascii")
                )
                data[ts.track.id] = track_data

            else:
                data[ts.track.id] = None

        return data


class TrackDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):

    model = Track
    template_name = "puzzle_hero/track_detail.html"

    def test_func(self):
        return user_is_player(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TrackDetail, self).get_context_data(**kwargs)

        team = self.request.user.player.team
        mission_statuses = MissionStatus.objects.filter(
            team=team,
            mission__track=self.object
        )

        post_statuses = PostStatus.objects.filter(
            team=team,
            post__mission__track=self.object
        )

        for ms in mission_statuses:
            ms.posts_completed = 0
            ms.post_total = 0

            for ps in post_statuses:
                if ps.post.mission == ms.mission:
                    if ps.status == "closed":
                        ms.posts_completed += 1
                    ms.post_total += 1

            ms.progress = ms.posts_completed / ms.post_total * 100

        tree_data = self._build_tree_data(mission_statuses)

        context['flag_form'] = FlagSubmissionForm()
        context['tree_data'] = tree_data
        context['announcements'] = TrackAnnouncement.objects.filter(
            track=self.object
        ).order_by('-time')
        context['mission_statuses'] = mission_statuses
        context['post_statuses'] = post_statuses

        return context

    def _build_tree_data(self, mission_statuses):
        data = {}

        for ms in mission_statuses:
            if ms.mission.track != self.object:
                continue

            mission_data = {}
            mission_data["title"] = ms.mission.title
            mission_data["status"] = ms.status
            mission_data["reward"] = ms.mission.reward

            dep_data = []
            for dep in ms.mission.dependencies.all():
                dep_data.append(dep.id)
            if len(dep_data) > 0:
                mission_data["dependencies"] = dep_data

            data[ms.mission.id] = mission_data

        data = base64.b64encode(
            json.dumps(data).encode("ascii")
        )

        return data


class MissionPage(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Mission
    context_object_name = 'mission'
    template_name = 'puzzle_hero/mission_page.html'

    def test_func(self):
        return user_is_player(self.request.user)

    def get_queryset(self):
        mission = Mission.objects.filter(id=self.kwargs.get('mission'))[0]
        mission.posts = Post.objects.filter(mission=mission)

        missions_status = MissionStatus.objects.filter(
            team=self.request.user.player.team,
            mission=mission
        ).first()
        mission.status = missions_status.status

        post_statuses = PostStatus.objects.filter(
            post__mission=mission,
            team=self.request.user.player.team
        )

        mission.posts_total = 0
        mission.posts_completed = 0

        for post in mission.posts:
            post.html_en = markdown.markdown(post.md_en)
            post.html_fr = markdown.markdown(post.md_fr)
            for ps in post_statuses:
                if ps.post == post:
                    post.status = ps.status
                    if ps.status == "closed":
                        mission.posts_completed += 1
                    mission.posts_total += 1
            post.announcements = PostAnnouncement.objects.filter(post=post).order_by('-time')

        mission.progress = mission.posts_completed / mission.posts_total * 100
        mission.announcements = MissionAnnouncement.objects.filter(
            mission=mission
        )

        return mission

    def get_context_data(self, **kwargs):
        context = super(MissionPage, self).get_context_data(**kwargs)
        context['flag_form'] = FlagSubmissionForm()

        context["nav"] = "mission_board"
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

    players = team.player_set.all().order_by("-score")
    for player in players:
        player.rank_level = player.rank_level()

    track_statuses = TrackStatus.objects.filter(team=team)
    completed_tracks = [ts.track for ts in track_statuses if ts.status in
                        [""
                         "", "closed"]]

    mission_statuses = MissionStatus.objects.filter(team=team)
    completed_missions = [ms.mission for ms in mission_statuses if ms.status in
                          ["closed"]]

    post_statuses = PostStatus.objects.filter(team=team)
    completed_posts = [ps.post for ps in post_statuses]

    teams = list(Team.objects.all().order_by("-score"))
    rank = teams.index(team) + 1

    context = {
        "team": team,
        "players": players,
        "tracks": completed_tracks,
        "missions": completed_missions,
        "posts": completed_posts,
        "team_rank": rank,
        "team_count": len(teams)
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


class GlobalAnnouncementList(LoginRequiredMixin, ListView):
    model = GlobalAnnouncement
    template_name = "puzzle_hero/announcements.html"
    context_object_name = "announcements"
    ordering = '-time'

    def get_context_data(self, **kwargs):
        context = super(GlobalAnnouncementList, self).get_context_data(**kwargs)
        context["nav"] = "announcements"
        return context



@login_required
@user_passes_test(user_is_csadmin)
def csadmin_index(request):
    return redirect("admin:index")


class CSAdminGlobalAnnouncementView(FormView):
    form_class = GlobalAnnouncementForm
    template_name = "cs_auth/login.html"
