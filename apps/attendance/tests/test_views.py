from datetime import date, timedelta
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.attendance.models import AttendanceRecord
from apps.interns.models import InternProfile


class AttendanceViewTests(APITestCase):
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
        InternProfile.objects.create(
            user=self.intern,
            school="Test School",
            phone="09171234567",
            start_date=date(2026, 3, 1),
            birthdate=date(2000, 1, 1),
        )

    @patch("apps.attendance.services.timezone.localtime")
    @patch("apps.attendance.services.timezone.localdate")
    def test_clock_in_success(self, mock_localdate, mock_localtime):
        mock_localdate.return_value = date(2026, 3, 23)
        mock_localtime.return_value = timezone.make_aware(
            timezone.datetime(2026, 3, 23, 8, 45)
        )
        self.client.force_authenticate(user=self.intern)

        response = self.client.post(reverse("attendance-clock-in"))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["record"]["status"], AttendanceRecord.StatusChoices.PRESENT)

    @patch("apps.attendance.services.timezone.localtime")
    @patch("apps.attendance.services.timezone.localdate")
    def test_duplicate_clock_in_rejected(self, mock_localdate, mock_localtime):
        today = date(2026, 3, 23)
        mock_localdate.return_value = today
        mock_localtime.return_value = timezone.make_aware(
            timezone.datetime(2026, 3, 23, 8, 45)
        )
        AttendanceRecord.objects.create(
            intern=self.intern,
            date=today,
            login_time=timezone.datetime(2026, 3, 23, 8, 45).time(),
            status=AttendanceRecord.StatusChoices.PRESENT,
        )
        self.client.force_authenticate(user=self.intern)

        response = self.client.post(reverse("attendance-clock-in"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "You have already clocked in today.")

    def test_classification_accuracy_for_admin_created_record(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("attendance-list"),
            {
                "intern": str(self.intern.id),
                "date": "2026-03-23",
                "login_time": "09:15:00",
                "logout_time": "16:30:00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], AttendanceRecord.StatusChoices.UNDERTIME)
        self.assertEqual(response.data["hours"], "7.25")

    def test_summary_format(self):
        monday = date(2026, 3, 23)
        AttendanceRecord.objects.create(
            intern=self.intern,
            date=monday,
            login_time=timezone.datetime(2026, 3, 23, 8, 45).time(),
            logout_time=timezone.datetime(2026, 3, 23, 17, 0).time(),
            hours="8.25",
            status=AttendanceRecord.StatusChoices.PRESENT,
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse("attendance-summary-weekly"),
            {"week_start": monday.isoformat()},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data[0]["date"], monday.isoformat())
        self.assertEqual(response.data[0]["present"], 1)

    def test_summary_invalid_week_start_returns_400(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse("attendance-summary-weekly"),
            {"week_start": "03-23-2026"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["errors"]["week_start"], ["Use YYYY-MM-DD format."])
