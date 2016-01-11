from django.core.exceptions import ValidationError

from .models import Team


def team_exists(value):
    if len(Team.objects.filter(token=value)) <= 0:
        raise ValidationError('%s is not a valid team token' % value)
