import django_filters

from apps.interns.models import InternProfile


class InternFilter(django_filters.FilterSet):
    batch = django_filters.UUIDFilter(field_name="batch_id")
    role = django_filters.CharFilter(field_name="intern_role")
    status = django_filters.CharFilter(field_name="user__status")
    assessment_completed = django_filters.BooleanFilter(method="filter_assessment_completed")

    class Meta:
        model = InternProfile
        fields = []

    def filter_assessment_completed(self, queryset, name, value):
        if value:
            return queryset.filter(assessment_completed_at__isnull=False)
        return queryset.filter(assessment_completed_at__isnull=True)
