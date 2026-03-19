from django.contrib import admin

from apps.interns.models import InternProfile, InternRegistrationRequest


@admin.register(InternProfile)
class InternProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "batch", "intern_role", "school", "required_hours", "rendered_hours")
    list_filter = ("intern_role", "assessment_required", "batch")
    search_fields = ("user__name", "user__email", "school", "github_username")


@admin.register(InternRegistrationRequest)
class InternRegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "status", "created_at", "decided_at")
    list_filter = ("status",)
    search_fields = ("name", "email", "school", "github_username")
