from django.contrib import admin

from apps.leaves.models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("intern", "from_date", "to_date", "type", "status", "business_days")
    list_filter = ("status", "type", "from_date", "to_date")
    search_fields = ("intern__email", "intern__name", "reason", "admin_note")
    ordering = ("-created_at",)
