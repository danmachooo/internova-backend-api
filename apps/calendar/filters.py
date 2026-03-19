import django_filters

from apps.calendar.models import CalendarEvent


class CalendarEventFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name="date")
    type = django_filters.CharFilter(field_name="type")

    class Meta:
        model = CalendarEvent
        fields = ["date", "type"]
