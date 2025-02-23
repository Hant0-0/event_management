import django_filters

from .models import EventParticipant


class EventParticipantFilter(django_filters.FilterSet):
    event = django_filters.NumberFilter(field_name="event", lookup_expr="exact")
    member = django_filters.NumberFilter(field_name="member", lookup_expr="exact")
    role = django_filters.CharFilter(field_name="role", lookup_expr="iexact")

    class Meta:
        model = EventParticipant
        fields = ['event', 'member', 'role']