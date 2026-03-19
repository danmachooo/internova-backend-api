from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from common.models import BaseModel


class Notification(BaseModel):
    class TypeChoices(models.TextChoices):
        INFO = "info", _("Info")
        WARNING = "warning", _("Warning")
        SUCCESS = "success", _("Success")
        ERROR = "error", _("Error")

    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(
        max_length=20,
        choices=TypeChoices.choices,
    )
    audience = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "notifications_notification"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["audience"], name="notifications_audience_idx"),
            models.Index(fields=["-created_at"], name="notifications_created_idx"),
        ]


class NotificationReadState(BaseModel):
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="read_states",
    )
    reader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_read_states",
    )
    read_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reader.email} - {self.notification.title}"

    class Meta:
        db_table = "notifications_notificationreadstate"
        ordering = ["-read_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["notification", "reader"],
                name="notifications_readstate_unique_notification_reader",
            )
        ]

