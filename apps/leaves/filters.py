import django_filters

from apps.leaves.models import LeaveRequest


class LeaveRequestFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(field_name="type")
    status = django_filters.CharFilter(field_name="status")
    from_date = django_filters.DateFilter(field_name="from_date", lookup_expr="gte")
    to_date = django_filters.DateFilter(field_name="to_date", lookup_expr="lte")

    class Meta:
        model = LeaveRequest
        fields = ["type", "status", "from_date", "to_date"]
