from django.contrib import messages

from .models import Submission, Trigger, TrackStatus, MissionStatus, PostStatus


def process_flag_submission(flag, request):
    player = request.user.player
    _create_submission(flag, player)
    _process_triggers(flag, request)


def _create_submission(flag, player):
    sub = Submission()
    sub.flag = flag
    sub.submitter = player
    sub.team = player.team
    sub.save()


def _process_triggers(flag, request):
    for trigger in flag.trigger_set.all():

        if trigger.kind == Trigger.TRACKSTATUS_TYPE:
            trigger = trigger.trackstatustrigger
            _process_trackstatus_trigger(trigger, request)

        elif trigger.kind == Trigger.MISSIONSTATUS_TYPE:
            trigger = trigger.missionstatustrigger
            _process_missionstatus_trigger(trigger, request)

        elif trigger.kind == Trigger.POSTSTATUS_TYPE:
            trigger = trigger.poststatustrigger
            _process_poststatus_trigger(trigger, request)

        elif trigger.kind == Trigger.TEAMSCORE_TYPE:
            trigger = trigger.teamscoretrigger
            _process_teamscore_trigger(trigger, request)


def _process_trackstatus_trigger(trigger, request):
    player = request.user.player
    track_status = TrackStatus.objects.filter(
        track=trigger.track,
        team=player.team
    )

    if not track_status:
        track_status = TrackStatus()
        track_status.team = player.team
        track_status.track = trigger.track
    else:
        track_status = track_status[0]
    track_status.status = trigger.status
    track_status.save()

    _process_track_dependencies(track_status.track, request)


def _process_missionstatus_trigger(trigger, request):
    player = request.user.player
    mission_status = MissionStatus.objects.filter(
        mission=trigger.mission,
        team=player.team
    )

    if not mission_status:
        mission_status = MissionStatus()
        mission_status.team = player.team
        mission_status.track = trigger.mission
    else:
        mission_status = mission_status[0]
    mission_status.status = trigger.status
    mission_status.save()

    _process_mission_dependencies(mission_status.mission, request)


def _process_poststatus_trigger(trigger, request):
    player = request.user.player
    post_status = PostStatus.objects.filter(
        post=trigger.post,
        team=player.team
    )

    if not post_status:
        post_status = PostStatus()
        post_status.team = player.team
        post_status.track = trigger.post
    else:
        post_status = post_status[0]
    post_status.status = trigger.status
    post_status.save()


def _process_teamscore_trigger(trigger, request):
    team = request.user.player.team
    team.score += trigger.score
    team.save()

    request.user.player.score += trigger.score
    request.user.player.save()


def _process_track_dependencies(track, request):
    team = request.user.player.team
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
            messages.add_message(
                request,
                messages.SUCCESS,
                'A new track has opened: %s!' % track_status.track.title
            )


def _process_mission_dependencies(mission, request):
    team = request.user.player.team
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
            messages.add_message(
                request,
                messages.SUCCESS,
                'New mission available: %s!' % mission_status.mission.title
            )

