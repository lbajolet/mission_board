from django.contrib import messages

from .models import Submission, Trigger, TrackStatus, MissionStatus, PostStatus, \
        Event, PlayerEvent, ScoreEvent


def process_flag_submission(flag, request=None, player=None, datetime=None):
    if request:
        _player = request.user.player
    if player:
        _player = player
    sub = _create_submission(flag, _player, datetime)
    _process_triggers(flag, sub)


def _create_submission(flag, player, datetime=None):
    sub = Submission()
    sub.flag = flag
    sub.submitter = player
    sub.team = player.team

    if datetime:
        sub.time = datetime
    sub.save()

    ev = PlayerEvent(
        player_event=True,
        type="flag_submission",
        message="Flag submitted!",
        player=player
    )
    ev.save()

    return sub


def _process_triggers(flag, sub, request=None):
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
            _process_teamscore_trigger(trigger, sub, request=request)


def _process_trackstatus_trigger(trigger, sub, request=None):

    track_status = TrackStatus.objects.filter(
        track=trigger.track,
        team=sub.team
    )

    if not track_status:
        track_status = TrackStatus()
        track_status.team = sub.team
        track_status.track = trigger.track
    else:
        track_status = track_status[0]
    track_status.status = trigger.status
    track_status.save()

    _process_track_dependencies(track_status.track, sub, request)


def _process_missionstatus_trigger(trigger, sub, request=None):

    mission_status = MissionStatus.objects.filter(
        mission=trigger.mission,
        team=sub.team
    )

    if not mission_status:
        mission_status = MissionStatus()
        mission_status.team = sub.team
        mission_status.track = trigger.mission
    else:
        mission_status = mission_status[0]
    mission_status.status = trigger.status
    mission_status.save()

    _process_mission_dependencies(mission_status.mission, sub, request)


def _process_poststatus_trigger(trigger, sub):

    post_status = PostStatus.objects.filter(
        post=trigger.post,
        team=sub.team
    )

    if not post_status:
        post_status = PostStatus()
        post_status.team = sub.team
        post_status.track = trigger.post
    else:
        post_status = post_status[0]
    post_status.status = trigger.status
    post_status.save()


def _process_teamscore_trigger(trigger, sub, request=None):

    team = sub.team
    team.score += trigger.score
    team.save()

    if request:
        request.user.score += trigger.score
        request.user.save()

        messages.add_message(
            request,
            messages.SUCCESS,
            'You have just earned %s points!' % trigger.score
        )

    if request:
        message = "%s of %s has scored %s points" % (request.user.display_name,
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

    if request:
        se.player_event = True
        se.player = request.user

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
            track_status.status = "open"
            track_status.save()
            if request:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'A new track has opened: %s!' % track_status.track.title
                )

            player = request.user.player
            ev = PlayerEvent(
                player_event=True,
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
            mission_status.status = "open"
            mission_status.save()

            if request:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'New mission available: %s!' % mission_status.mission.title
                )

                player = request.user.player
                ev = PlayerEvent(
                    player_event=True,
                    type="mission_unlock",
                    message="%s unlocked" % mission_status.mission.title,
                    player=player
                )
                ev.save()
