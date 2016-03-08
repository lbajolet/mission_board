import json
import base64
import math
import time

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import logout
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView, FormView, DetailView

from cs_auth.models import Team

from .forms import FlagSubmissionForm, AdminFlagSubmissionForm, \
    AdminGlobalSubmissionForm
from .models import Mission, MissionStatus, Post, PostStatus, Track, \
    TrackStatus, Submission, Flag, GlobalAnnouncement, TeamAnnouncement, \
    TrackAnnouncement, MissionAnnouncement, PostAnnouncement, Event, \
    PlayerEvent, Trigger, TeamScoreTrigger, GlobalStatus, ScoreEvent, \
    BadFlagEvent
from .triggers import process_flag_submission

import json
import markdown


# Used as test function to in several auths on views
def user_is_player(user):
    return hasattr(user, "player")


def user_is_csadmin(user):
    return user.is_superuser


def global_status_ok(function=None):

    def _decorator(view_function):
        def _view(request, *args, **kwargs):
            gs = GlobalStatus.objects.all().first()

            if not gs:
                message = "Mission Board is not accessible yet!"
                return render(request, "puzzle_hero/global_status.html",
                              context={"message": message})

            if gs.status == "closed":
                message = "Missions have been completed!"
                return render(request, "puzzle_hero/global_status.html",
                              context={"message": message})

            if gs.paused:
                message = ("We might have been spotted! "
                           "You must refrain from accomplishing "
                           "missions for now.")
                return render(request, "puzzle_hero/global_status.html",
                              context={"message": message})

            else:
                return view_function(request, *args, **kwargs)
        return _view

    if function is None:
        return _decorator
    else:
        return _decorator(function)


def global_status_scoreboard(function=None):

    def _decorator(view_function):
        def _view(request, *args, **kwargs):
            gs = GlobalStatus.objects.all().first()

            if not gs:
                message = "Mission Board is not accessible yet!"
                return render(request, "puzzle_hero/global_status.html",
                              context={"message": message})

            if gs.scoreboard_hidden:
                message = "The scoreboard is not available for now!"
                return render(request, "puzzle_hero/global_status.html",
                              context={"message": message})

            else:
                return view_function(request, *args, **kwargs)
        return _view

    if function is None:
        return _decorator
    else:
        return _decorator(function)


class TracksList(LoginRequiredMixin, ListView):

    model = TrackStatus
    context_object_name = 'track_statuses'
    template_name = 'puzzle_hero/tracks_list.html'

    def get_queryset(self):
        print(self.request.COOKIES)
        team = self.request.user.player.team

        track_statuses = TrackStatus.objects.filter(team=team).order_by('-track__id')
        for track_status in track_statuses:
            track_status.track.missions = Mission.objects.filter(track=track_status.track)

        return track_statuses

    def get_context_data(self, **kwargs):
        context = super(TracksList, self).get_context_data(**kwargs)
        context['flag_form'] = FlagSubmissionForm()

        team = self.request.user.player.team
        track_statuses = TrackStatus.objects.filter(team=team)
        mission_statuses = MissionStatus.objects.filter(team=team)
        context["mission_statuses"] = mission_statuses

        tree_data = self._build_tree_data(track_statuses, mission_statuses)
        context["tree_data"] = tree_data

        context["team_announcements"] = TeamAnnouncement.objects.filter(team=team).order_by("-time")

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
                    mission_data["kind"] = ms.mission.kind

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

class MobileTrackList(TracksList):
    login_url = "/auth/mobile_login"

    template_name = 'puzzle_hero/mobile_tracks_list.html'


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
        context['status'] = TrackStatus.objects.filter(track=self.object,
                                                       team=team).first().status

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
            mission_data["kind"] = ms.mission.kind

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


class Scoreboard(ListView):
    model = Team
    context_object_name = 'teams'
    template_name = 'puzzle_hero/scoreboard.html'

    def test_func(self):
        return user_is_player(self.request.user)

    def get_queryset(self):
        return Team.objects.all().order_by("-score")

    def get_context_data(self, **kwargs):
        context = super(Scoreboard, self).get_context_data(**kwargs)
        context["nav"] = "scoreboard"

        graph_data = self.build_graph_data()
        context["scoreboard"] = base64.b64encode(
            json.dumps(graph_data).encode("ascii")
        )

        return context

    @staticmethod
    def build_graph_data():

        gs = GlobalStatus.objects.all().first()
        min_date = gs.start_time.timestamp()

        if gs.end_time:
            max_date = gs.end_time.timestamp()
        else:
            max_date = timezone.now().timestamp()


        team_dict = {}
        teams = Team.objects.all().order_by("-score")

        min_score = 0
        max_score = math.ceil(teams[0].score / 100) * 100

        for team in teams:
            if team.hidden:
                continue

            team_dict[team.name] = {
                "id": team.id,
                "name": team.name,
                "color": team.color,
                "scores": [{
                    "team": team.name,
                    "timestamp": min_date,
                    "score": 0
                }]
            }

        score_events = ScoreEvent.objects.all()

        for se in score_events:
            if se.team.hidden:
                continue

            timestamp = se.time
            timestamp = int(timestamp.timestamp())
            new_score = {
                "id": se.team.id,
				"name": se.team.name,
                "timestamp": timestamp,
                "score": se.score_total
            }
            team_dict[se.team.name]["scores"].append(new_score)

        data = {
            "minDate": min_date,
            "maxDate": max_date,
            "minScore": min_score,
            "maxScore": max_score,
            "teams": []
        }

        for k, v in team_dict.items():
            data["teams"].append(v)

        return data


@login_required
@user_passes_test(user_is_player)
def team_stats(request, team_id):
    team = Team.objects.filter(id=team_id)[0]

    players = team.player_set.all().order_by("-score")
    for player in players:
        player.rank_level = player.rank_level()

    track_statuses = TrackStatus.objects.filter(team=team)
    completed_tracks = [ts.track for ts in track_statuses if ts.status in
                        ["closed"]]

    mission_statuses = MissionStatus.objects.filter(team=team)
    completed_missions = [ms.mission for ms in mission_statuses if ms.status in
                          ["closed"]]

    post_statuses = PostStatus.objects.filter(team=team)
    completed_posts = [ps.post for ps in post_statuses]

    teams = list(Team.objects.all().order_by("-score"))
    rank = teams.index(team) + 1

    for ts in track_statuses:
        ts.miss_completed = 0
        ts.miss_total = 0

        for ms in mission_statuses:
            if ms.mission.track == ts.track:
                if ms.status == 'closed':
                    ts.miss_completed += 1
                ts.miss_total += 1

        ts.progress = ts.miss_completed / ts.miss_total * 100

    events = PlayerEvent.objects.filter(
        player__team=team,
    ).order_by('-time')

    context = {
        "team": team,
        "players": players,
        "tracks": completed_tracks,
        "missions": completed_missions,
        "posts": completed_posts,
        "team_rank": rank,
        "team_count": len(teams),
        "track_statuses": track_statuses,
        "events": events,
    }

    return render(request, "puzzle_hero/team_stats.html", context)


@login_required
@user_passes_test(user_is_player)
def submit_flag(request):
    print(request.COOKIES)
    if request.method == 'POST' or request.method == 'GET':
        player = request.user.player
        if request.method == 'POST':
            form = FlagSubmissionForm(request.POST)
        else:
            form = FlagSubmissionForm(request.GET)
        if form.is_valid():
            # Check if flag has already been submitted:
            flag_token = form.cleaned_data["token"]
            flag = Flag.objects.filter(token=flag_token).first()

            subs = Submission.objects.filter(flag=flag,
                                             team=player.team)

            # Flag has already been submitted by this team
            if subs:
                message = "This flag has already been submitted."
                messages.add_message(
                    request,
                    messages.WARNING,
                    message
                )
                if request.method == 'GET':
                    return JsonResponse({'result': 'warning', 'message': message})
                else:
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER',
                                                                 reverse_lazy('tracklist')))

            else:
                message = 'Submitted flag %s!' % form.cleaned_data["token"]
                process_flag_submission(flag, request=request)
                player = request.user.player
                player.bad_flag_count = 0
                player.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    message
                )
                if request.method == 'GET':
                    return JsonResponse({'result': 'success', 'message': message})
                else:
                    if request.META.get('HTTP_REFERER', None):
                        return HttpResponseRedirect(request.META['HTTP_REFERER'])
                    else:
                        return HttpResponseRedirect(reverse_lazy('tracklist'))

        else:

            wrong_flag = form.data["token"]

            player = request.user.player
            player.bad_flag_count += 1

            bfe = BadFlagEvent(
                is_player_event=True,
                type="bad_flag",
                message="%s submitted a bad flag: %s" % (player, wrong_flag),
                token=wrong_flag,
                player=player
            )

            bfe.save()

            if player.bad_flag_count > 50:
                player.bad_flag_count = 0
                player.user.is_active = False
                player.user.save()
                logout(request)

            player.save()

            message = 'Invalid flag %s !' % wrong_flag
            messages.add_message(request, messages.ERROR,
                                 message)
            if request.method == 'GET':
                return JsonResponse({'result': 'error', 'message': message})
            else:
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
def admin_panel(request):

    context = {}

    gs = GlobalStatus.objects.first()
    context["global_status"] = gs

    flag_form = AdminFlagSubmissionForm()
    context['flag_form'] = flag_form

    global_flag_form = AdminGlobalSubmissionForm()
    context['global_flag_form'] = global_flag_form

    return render(request, template_name="puzzle_hero/admin_panel.html",
                  context=context)


@login_required
@user_passes_test(user_is_csadmin)
def admin_dashboard(request):
    context = {}

    # Latest scoring
    latest_scores = ScoreEvent.objects.all().order_by("-time")[0:4]
    context["latest_scores"] = latest_scores

    # Latest announcement
    latest_ann = GlobalAnnouncement.objects.all().order_by("-time").first()
    context["latest_announcement"] = latest_ann

    # Latest events
    latest_ev = Event.objects.all().order_by("-time")[0:4]
    context["latest_events"] = latest_ev

    # Tracks
    tracks = Track.objects.all()
    mission_statuses = MissionStatus.objects.all()

    for track in tracks:

        track.closed_count = 0
        track.locked_count = 0
        track.open_count = 0
        track.total_statuses = 0

        for ms in mission_statuses:
            # Not the right track
            if ms.mission.track != track:
                continue

            track.total_statuses += 1

            if ms.status == "closed":
                track.closed_count += 1

            elif ms.status == "open":
                track.open_count += 1

            elif ms.status == "locked":
                track.locked_count += 1

        track.closed_percent = track.closed_count * 100 / track.total_statuses
        track.open_percent = track.open_count * 100 / track.total_statuses
        track.locked_percent = track.locked_count * 100 / track.total_statuses

    context["tracks"] = tracks

    # Scoreboard yo
    graph_data = Scoreboard.build_graph_data()
    context["scoreboard"] = base64.b64encode(
        json.dumps(graph_data).encode("ascii")
    )

    return render(request, "puzzle_hero/admin_dashboard.html", context)


@login_required
@user_passes_test(user_is_csadmin)
def admin_submit_flag(request):

    if request.method == "POST":
        form = AdminFlagSubmissionForm(request.POST)
        if form.is_valid():
            flag_token = form.cleaned_data["token"]
            team = form.cleaned_data["team"]
            flag = Flag.objects.filter(token=flag_token).first()
            subs = Submission.objects.filter(flag=flag, team=team)

            if subs:
                messages.add_message(
                    request,
                    messages.WARNING,
                    "This flag has already been submitted by this team."
                )

            else:
                process_flag_submission(flag, team=team)
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Submitted flag %s for %s!' % (flag_token, team)
                )

        else:
            wrong_flag = form.data["token"]
            messages.add_message(request, messages.ERROR,
                                 'Invalid flag %s !' % wrong_flag)

    return HttpResponseRedirect(reverse_lazy("admin_panel"))


@login_required
@user_passes_test(user_is_csadmin)
def admin_global_submit_flag(request):

    if request.method == "POST":
        form = FlagSubmissionForm(request.POST)
        if form.is_valid():
            flag_token = form.cleaned_data["token"]
            flag = Flag.objects.filter(token=flag_token).first()

            teams = Team.objects.all()
            for team in teams:
                subs = Submission.objects.filter(flag=flag, team=team)
                if not subs:
                    process_flag_submission(flag, team=team)

        else:
            wrong_flag = form.data["token"]
            messages.add_message(request, messages.ERROR,
                                 'Invalid flag %s !' % wrong_flag)

    return HttpResponseRedirect(reverse_lazy("admin_panel"))
