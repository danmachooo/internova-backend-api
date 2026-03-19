from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.notifications.models import Notification, NotificationReadState


class NotificationViewTests(APITestCase):
    def setUp(self):
        self.superadmin = User.objects.create_user(
            email="superadmin@example.com",
            name="Super Admin",
            password="StrongPass123!",
            role=User.RoleChoices.SUPERADMIN,
        )
        self.staffadmin = User.objects.create_user(
            email="staffadmin@example.com",
            name="Staff Admin",
            password="StrongPass123!",
            role=User.RoleChoices.STAFFADMIN,
        )
        self.intern = User.objects.create_user(
            email="intern@example.com",
            name="Intern User",
            password="StrongPass123!",
            role=User.RoleChoices.INTERN,
        )
        self.other_intern = User.objects.create_user(
            email="other@example.com",
            name="Other Intern",
            password="StrongPass123!",
            role=User.RoleChoices.INTERN,
        )
        self.all_notification = Notification.objects.create(
            title="All Hands",
            message="Everyone sees this.",
            type=Notification.TypeChoices.INFO,
            audience="all",
        )
        self.admin_notification = Notification.objects.create(
            title="Admin Notice",
            message="Admins see this.",
            type=Notification.TypeChoices.WARNING,
            audience="admin",
        )
        self.intern_notification = Notification.objects.create(
            title="Intern Notice",
            message="Interns see this.",
            type=Notification.TypeChoices.SUCCESS,
            audience="intern",
        )
        self.specific_notification = Notification.objects.create(
            title="Specific Notice",
            message="One intern sees this.",
            type=Notification.TypeChoices.ERROR,
            audience=f"intern:{self.intern.id}",
        )

    def test_admin_list_filters_to_admin_audiences(self):
        self.client.force_authenticate(user=self.staffadmin)

        response = self.client.get(reverse("notification-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        returned_ids = {item["id"] for item in response.data["results"]}
        self.assertSetEqual(
            returned_ids,
            {str(self.all_notification.id), str(self.admin_notification.id)},
        )

    def test_intern_list_filters_to_intern_audiences(self):
        self.client.force_authenticate(user=self.intern)

        response = self.client.get(reverse("notification-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        returned_ids = {item["id"] for item in response.data["results"]}
        self.assertSetEqual(
            returned_ids,
            {
                str(self.all_notification.id),
                str(self.intern_notification.id),
                str(self.specific_notification.id),
            },
        )

    def test_mark_read_sets_read_flag_for_current_user(self):
        self.client.force_authenticate(user=self.intern)

        response = self.client.post(
            reverse("notification-read", kwargs={"pk": self.specific_notification.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["read"])
        self.assertTrue(
            NotificationReadState.objects.filter(
                notification=self.specific_notification,
                reader=self.intern,
            ).exists()
        )

    def test_admin_can_create_notification(self):
        self.client.force_authenticate(user=self.superadmin)

        response = self.client.post(
            reverse("notification-list"),
            {
                "title": "Launch",
                "message": "The new dashboard is live.",
                "type": Notification.TypeChoices.SUCCESS,
                "audience": "all",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 5)

    def test_intern_cannot_create_notification(self):
        self.client.force_authenticate(user=self.intern)

        response = self.client.post(
            reverse("notification-list"),
            {
                "title": "Hack",
                "message": "Nope.",
                "type": Notification.TypeChoices.INFO,
                "audience": "all",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_notification(self):
        self.client.force_authenticate(user=self.staffadmin)

        response = self.client.delete(
            reverse("notification-detail", kwargs={"pk": self.all_notification.id})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Notification.objects.filter(pk=self.all_notification.id).exists())

    def test_intern_cannot_delete_notification(self):
        self.client.force_authenticate(user=self.intern)

        response = self.client.delete(
            reverse("notification-detail", kwargs={"pk": self.all_notification.id})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_read_returns_404_for_hidden_notification(self):
        hidden_notification = Notification.objects.create(
            title="Hidden",
            message="Only for another intern.",
            type=Notification.TypeChoices.INFO,
            audience=f"intern:{self.other_intern.id}",
        )
        self.client.force_authenticate(user=self.intern)

        response = self.client.post(
            reverse("notification-read", kwargs={"pk": hidden_notification.id})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
