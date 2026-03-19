from django.db import transaction

from apps.notifications.models import Notification, NotificationReadState


class NotificationService:
    @staticmethod
    def push(*, title, message, audience, type):
        return Notification.objects.create(
            title=title,
            message=message,
            audience=audience,
            type=type,
        )

    @staticmethod
    @transaction.atomic
    def mark_read(*, notification, reader):
        read_state, _ = NotificationReadState.objects.get_or_create(
            notification=notification,
            reader=reader,
        )
        return read_state

