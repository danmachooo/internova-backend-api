import django_filters

from apps.batches.models import Batch


class BatchFilter(django_filters.FilterSet):
    class Meta:
        model = Batch
        fields = {
            "status": ["exact"],
        }
