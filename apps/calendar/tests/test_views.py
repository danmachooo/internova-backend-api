from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.calendar.models import CalendarEvent, CalendarSettings, Holiday


class CalendarViewTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com",
            name="Admin User",
            password="StrongPass123!",
            role=User.RoleChoices.STAFFADMIN,
        )
        self.intern = User.objects.create_user(
            email="intern@example.com",
            name="Intern User",
            password="StrongPass123!",
            role=User.RoleChoices.INTERN,
        )
        CalendarSettings.get()

    def test_admin_can_create_calendar_event(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("event-list"),
            {
                "title": "Sprint Review",
                "date": "2026-03-24",
                "time": "10:00:00",
                "type": "meeting",
                "description": "Weekly review",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CalendarEvent.objects.count(), 1)

    def test_intern_can_list_events(self):
        CalendarEvent.objects.create(
            title="Demo Day",
            date=date(2026, 3, 24),
            time="13:00:00",
            type=CalendarEvent.TypeChoices.PRESENTATION,
            description="Team demos",
        )
        self.client.force_authenticate(user=self.intern)

        response = self.client.get(reverse("event-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_admin_can_update_calendar_settings(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse("calendar-settings"),
            {"weekend_days": [5, 6]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["weekend_days"], [5, 6])

    def test_intern_cannot_update_calendar_settings(self):
        self.client.force_authenticate(user=self.intern)

        response = self.client.patch(
            reverse("calendar-settings"),
            {"weekend_days": [5, 6]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_and_delete_holiday(self):
        self.client.force_authenticate(user=self.admin)

        create_response = self.client.post(
            reverse("holiday-list"),
            {"date": "2026-12-25", "name": "Christmas Day"},
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        holiday_id = create_response.data["id"]

        delete_response = self.client.delete(reverse("holiday-detail", kwargs={"pk": holiday_id}))

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Holiday.objects.exists())
