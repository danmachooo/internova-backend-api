import django_filters

from apps.accounts.models import User


class AdminUserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            "role": ["exact"],
            "status": ["exact"],
        }
