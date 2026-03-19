from django.contrib import admin

from apps.attendance.models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("intern", "date", "login_time", "logout_time", "hours", "status")
    list_filter = ("status", "date")
    search_fields = ("intern__email", "intern__name")
    ordering = ("-date",)
