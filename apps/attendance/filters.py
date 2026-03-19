import django_filters

from apps.attendance.models import AttendanceRecord


class AttendanceFilter(django_filters.FilterSet):
    intern = django_filters.UUIDFilter(field_name="intern_id")
    date = django_filters.DateFilter(field_name="date")
    status = django_filters.CharFilter(field_name="status")

    class Meta:
        model = AttendanceRecord
        fields = ("intern", "date", "status")
