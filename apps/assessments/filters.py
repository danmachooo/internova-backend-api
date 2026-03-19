import django_filters

from apps.assessments.models import Assessment, InternAttempt


class AssessmentFilter(django_filters.FilterSet):
    is_published = django_filters.BooleanFilter()

    class Meta:
        model = Assessment
        fields = ("is_published",)


class InternAttemptFilter(django_filters.FilterSet):
    assessment = django_filters.UUIDFilter(field_name="assessment_id")
    completed = django_filters.BooleanFilter()

    class Meta:
        model = InternAttempt
        fields = ("assessment", "completed")
