from django.contrib import messages
from django.core.urlresolvers import reverse_lazy


from .models import Submission, Trigger, TrackStatus, MissionStatus, PostStatus, \
        Event, PlayerEvent, ScoreEvent


def process_flag_submission(flag, request=None, player=None, team=None,
                            datetime=None):

    sub = None
    if request:
        player = request.user.player
        sub = _create_submission(flag, player=player, datetime=datetime)
        _process_triggers(flag, sub, request=request, player=player)
    elif player:
        sub = _create_submission(flag, player=player, datetime=datetime)
        _process_triggers(flag, sub, player=player)
    elif team:
        sub = _create_submission(flag, team=team, datetime=datetime)
        _process_triggers(flag, sub, player=player)


def _create_submission(flag, player=None, team=None, datetime=None):
    sub = Submission()
    sub.flag = flag
    if player:
        sub.submitter = player
        sub.team = player.team
    else:
        sub.team = team

    if datetime:
        sub.time = datetime
    sub.save()

    if player:
        ev = PlayerEvent(
            is_player_event=True,
            type="flag_submission",
            message="Flag submitted!",
            player=player
        )
    else:
        ev = Event(
            type="flag_submission",
            message="Flag submitted by %s!" % team.name,
        )
    ev.save()

    return sub


def _process_triggers(flag, sub, player=None, request=None):

    for trigger in flag.trigger_set.all():

        if trigger.kind == Trigger.TRACKSTATUS_TYPE:
            trigger = trigger.trackstatustrigger
            _process_trackstatus_trigger(trigger, sub, request=request)

        elif trigger.kind == Trigger.MISSIONSTATUS_TYPE:
            trigger = trigger.missionstatustrigger
            _process_missionstatus_trigger(trigger, sub, request=request)

        elif trigger.kind == Trigger.POSTSTATUS_TYPE:
            trigger = trigger.poststatustrigger
            _process_poststatus_trigger(trigger, sub)

        elif trigger.kind == Trigger.TEAMSCORE_TYPE:
            trigger = trigger.teamscoretrigger
            _process_teamscore_trigger(trigger, sub, player, request=request)


def _process_trackstatus_trigger(trigger, sub, request=None):

    track_status = TrackStatus.objects.filter(
        track=trigger.track,
        team=sub.team
    ).first()

    if track_status.status != "closed":

        if track_status.status == "locked" and trigger.status == "open":
            if request:
                link = """<a href="%s">%s</a>""" % (
                    reverse_lazy("track_detail", kwargs={
                        "pk": track_status.track.id
                    }), track_status.track.title
                )

                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'A new track has opened: %s!' % link
                )

        track_status.status = trigger.status
        track_status.save()

    _process_track_dependencies(track_status.track, sub, request)


def _process_missionstatus_trigger(trigger, sub, request=None):

    mission_status = MissionStatus.objects.filter(
        mission=trigger.mission,
        team=sub.team
    ).first()

    if trigger.status == 'closed':
        mission = mission_status.mission
        track = mission.track
        track_status = TrackStatus.objects.filter(track=track,
                                                  team=sub.team).first()
        if track_status.status == 'locked':
            track_status.status = 'open'
            track_status.save()

    if mission_status.status != "closed":

        mission_status.status = trigger.status
        mission_status.save()

        team = sub.team
        team.score += trigger.mission.reward
        team.save()

        if request:
            request.user.player.score += trigger.mission.reward
            request.user.player.save()

        se = ScoreEvent(
            time=sub.time,
            type="score_event",
            message="Finished mission %s!" % trigger.mission.title,
            score_delta=trigger.mission.reward,
            score_total=team.score,
            team=team
        )

        if sub.submitter:
            se.is_player_event = True
            se.player = sub.submitter
        se.save()

    _process_mission_dependencies(mission_status.mission, sub, request)


def _process_poststatus_trigger(trigger, sub):

    post_status = PostStatus.objects.filter(
        post=trigger.post,
        team=sub.team
    ).first()

    if post_status.status != "closed":
        post_status.status = trigger.status
        post_status.save()


def _process_teamscore_trigger(trigger, sub, player=None, request=None):

    team = sub.team
    team.score += trigger.score
    team.save()

    if request:
        player = request.user.player

    if player:
        player.score += trigger.score
        player.save()

    if request:
        messages.add_message(
            request,
            messages.SUCCESS,
            'You have just earned %s points!' % trigger.score
        )

    if player:
        message = "%s of %s has scored %s points" % (player.display_name,
                                                     sub.team.name,
                                                     trigger.score)
    else:
        message = "%s has scored %s points" % (sub.team.name,
                                               trigger.score)

    se = ScoreEvent(
        time=sub.time,
        type="score_event",
        message=message,
        score_delta=trigger.score,
        score_total=team.score,
        team=team
    )

    if player:
        se.is_player_event = True
        se.player = player

    se.save()


def _process_track_dependencies(track, sub, request=None):
    team = sub.team
    affected_tracks = track.required_for.all()
    for affected_track in affected_tracks:
        dependencies = affected_track.dependencies.all()
        solved_deps = TrackStatus.objects.filter(team=team,
                                                 status="closed",
                                                 track__in=dependencies,
                                                 )
        if len(solved_deps) == len(dependencies):
            track_status = TrackStatus.objects.filter(team=team,
                                                      track=affected_track)

            if track_status.status != "closed":
                track_status.status = "open"
                track_status.save()

                if request:
                    link = """<a href="%s">%s</a>""" % (
                        reverse_lazy("track_detail", kwargs={
                            "pk": track_status.track.id
                        }), track_status.track.title
                    )

                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        'A new track has opened: %s!' % link
                    )

                player = request.user.player
                ev = PlayerEvent(
                    is_player_event=True,
                    type="track_unlock",
                    message="%s unlocked" % track_status.track.title,
                    player=player
                )
                ev.save()


def _process_mission_dependencies(mission, sub, request=None):
    team = sub.team
    affected_missions = mission.required_for.all()
    for affected_mission in affected_missions:
        dependencies = affected_mission.dependencies.all()
        solved_deps = MissionStatus.objects.filter(team=team,
                                                   status="closed",
                                                   mission__in=dependencies,
                                                   )
        if len(solved_deps) == len(dependencies):
            mission_status = MissionStatus.objects.filter(
                team=team,
                mission=affected_mission
            ).first()
            if mission_status.status != "closed":
                mission_status.status = "open"
                mission_status.save()

                if request:
                    link = """<a href="%s">%s</a>""" % (
                        reverse_lazy("mission_page", kwargs={
                            "mission": mission_status.mission.id
                        }),
                        mission_status.mission.title
                    )

                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        'New mission available: %s!' % link
                    )

                    player = request.user.player
                    ev = PlayerEvent(
                        is_player_event=True,
                        type="mission_unlock",
                        message="%s unlocked" % mission_status.mission.title,
                        player=player
                    )
                    ev.save()
