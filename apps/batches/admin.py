from django.contrib import admin

from apps.batches.models import Batch


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "progress", "start_date", "end_date")
    list_filter = ("status",)
    search_fields = ("name",)
    ordering = ("-start_date",)
