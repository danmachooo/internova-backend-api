from django.db import IntegrityError
from django.test import TestCase

from apps.accounts.models import User
from apps.notifications.models import Notification, NotificationReadState


class NotificationModelTests(TestCase):
    def setUp(self):
        self.reader = User.objects.create_user(
            email="reader@example.com",
            name="Reader User",
            password="StrongPass123!",
            role=User.RoleChoices.INTERN,
        )
        self.notification = Notification.objects.create(
            title="Welcome",
            message="Welcome aboard",
            type=Notification.TypeChoices.INFO,
            audience="intern",
        )

    def test_notification_defaults_to_latest_first_ordering(self):
        newer = Notification.objects.create(
            title="System Update",
            message="A newer notification",
            type=Notification.TypeChoices.SUCCESS,
            audience="all",
        )

        notifications = list(Notification.objects.values_list("id", flat=True))

        self.assertEqual(notifications[0], newer.id)
        self.assertEqual(notifications[1], self.notification.id)

    def test_notification_read_state_unique_per_reader_and_notification(self):
        NotificationReadState.objects.create(
            notification=self.notification,
            reader=self.reader,
        )

        with self.assertRaises(IntegrityError):
            NotificationReadState.objects.create(
                notification=self.notification,
                reader=self.reader,
            )

