from django.contrib import admin

from apps.feature_access.models import FeatureAccessConfig


@admin.register(FeatureAccessConfig)
class FeatureAccessConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "updated_at")

