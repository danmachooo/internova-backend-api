from django.contrib import admin

from apps.assets.models import Laptop, LaptopIssueReport


@admin.register(Laptop)
class LaptopAdmin(admin.ModelAdmin):
    list_display = ("brand", "serial_no", "assigned_to", "status", "ip_address")
    list_filter = ("status",)
    search_fields = ("brand", "serial_no", "accounts", "assigned_to__email", "assigned_to__name")
    ordering = ("brand", "serial_no")


@admin.register(LaptopIssueReport)
class LaptopIssueReportAdmin(admin.ModelAdmin):
    list_display = ("intern", "laptop", "status", "resolved_by", "resolved_at")
    list_filter = ("status", "created_at")
    search_fields = ("intern__email", "intern__name", "laptop__serial_no", "description", "admin_note")
    ordering = ("-created_at",)
