from django.contrib import admin

from apps.projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "start_date", "end_date")
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("name", "description")
    ordering = ("name",)
    filter_horizontal = ("assigned_interns",)
