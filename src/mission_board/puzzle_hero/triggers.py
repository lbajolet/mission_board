from .models import Submission, Trigger, TrackStatus, MissionStatus, PostStatus


def process_flag_submission(flag, player):
    _create_submission(flag, player)
    _process_triggers(flag, player)


def _create_submission(flag, player):
    sub = Submission()
    sub.flag = flag
    sub.submitter = player
    sub.team = player.team
    sub.save()


def _process_triggers(flag, player):
    for trigger in flag.trigger_set.all():

        if trigger.kind == Trigger.TRACKSTATUS_TYPE:
            trigger = trigger.trackstatustrigger
            _process_trackstatus_trigger(trigger, player)

        elif trigger.kind == Trigger.MISSIONSTATUS_TYPE:
            trigger = trigger.missionstatustrigger
            _process_missionstatus_trigger(trigger, player)

        elif trigger.kind == Trigger.POSTSTATUS_TYPE:
            trigger = trigger.poststatustrigger
            _process_poststatus_trigger(trigger, player)

        elif trigger.kind == Trigger.TEAMSCORE_TYPE:
            trigger = trigger.teamscoretrigger
            _process_teamscore_trigger(trigger, player)


def _process_trackstatus_trigger(trigger, player):
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

    _process_track_dependencies(track_status.track, player.team)


def _process_missionstatus_trigger(trigger, player):
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


def _process_poststatus_trigger(trigger, player):
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


def _process_teamscore_trigger(trigger, player):
    team = player.team
    team.score += trigger.score
    team.save()

def _process_track_dependencies(track, team):
    affected_tracks = track.required_for
