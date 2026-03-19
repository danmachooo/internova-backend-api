from django.contrib import admin

from apps.notifications.models import Notification, NotificationReadState


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "audience", "created_at")
    search_fields = ("title", "message", "audience")
    list_filter = ("type", "created_at")
    ordering = ("-created_at",)


@admin.register(NotificationReadState)
class NotificationReadStateAdmin(admin.ModelAdmin):
    list_display = ("notification", "reader", "read_at")
    search_fields = ("notification__title", "reader__email")
    ordering = ("-read_at",)

