from django.test import TestCase

from apps.accounts.models import User
from apps.notifications.models import Notification, NotificationReadState
from apps.notifications.services import NotificationService


class NotificationServiceTests(TestCase):
    def setUp(self):
        self.reader = User.objects.create_user(
            email="reader@example.com",
            name="Reader User",
            password="StrongPass123!",
            role=User.RoleChoices.INTERN,
        )
        self.notification = Notification.objects.create(
            title="Reminder",
            message="Submit your DAR.",
            type=Notification.TypeChoices.WARNING,
            audience=f"intern:{self.reader.id}",
        )

    def test_push_creates_notification(self):
        notification = NotificationService.push(
            title="Approved",
            message="Your request has been approved.",
            audience="intern",
            type=Notification.TypeChoices.SUCCESS,
        )

        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(notification.title, "Approved")

    def test_mark_read_is_idempotent(self):
        first = NotificationService.mark_read(
            notification=self.notification,
            reader=self.reader,
        )
        second = NotificationService.mark_read(
            notification=self.notification,
            reader=self.reader,
        )

        self.assertEqual(first.id, second.id)
        self.assertEqual(NotificationReadState.objects.count(), 1)

