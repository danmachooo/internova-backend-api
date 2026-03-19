from django.contrib import admin

from apps.dar.models import DailyActivityReport


@admin.register(DailyActivityReport)
class DailyActivityReportAdmin(admin.ModelAdmin):
    list_display = ("intern", "date", "upload_time", "status")
    list_filter = ("status", "date")
    search_fields = ("intern__email", "intern__name")
    ordering = ("-date", "-created_at")
