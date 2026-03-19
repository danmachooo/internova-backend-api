from django.contrib import admin

from apps.calendar.models import CalendarEvent, CalendarSettings, Holiday


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "time", "type")
    list_filter = ("type", "date")
    search_fields = ("title", "description")
    ordering = ("date", "time")


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ("name", "date")
    search_fields = ("name",)
    ordering = ("date",)


@admin.register(CalendarSettings)
class CalendarSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "weekend_days", "updated_at")
