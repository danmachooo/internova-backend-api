from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.calendar.models import CalendarSettings
from apps.leaves.models import LeaveRequest
from apps.interns.models import InternProfile


class LeaveRequestViewTests(APITestCase):
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
        self.other_intern = User.objects.create_user(
            email="other@example.com",
            name="Other Intern",
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
        InternProfile.objects.create(
            user=self.other_intern,
            school="Test School",
            phone="09170000000",
            start_date=date(2026, 3, 1),
            birthdate=date(2000, 2, 2),
        )
        CalendarSettings.get()

    def test_intern_can_submit_leave_with_computed_business_days(self):
        self.client.force_authenticate(user=self.intern)

        response = self.client.post(
            reverse("leave-list"),
            {
                "from_date": "2026-03-23",
                "to_date": "2026-03-24",
                "type": "sick",
                "reason": "Fever",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["business_days"], 2)

    def test_admin_can_approve_leave(self):
        leave = LeaveRequest.objects.create(
            intern=self.intern,
            from_date=date(2026, 3, 23),
            to_date=date(2026, 3, 24),
            business_days=2,
            type=LeaveRequest.LeaveTypeChoices.SICK,
            reason="Fever",
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("leave-approve", kwargs={"pk": leave.id}),
            {"admin_note": "Get well soon."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], LeaveRequest.StatusChoices.APPROVED)

    def test_admin_can_deny_leave_with_note(self):
        leave = LeaveRequest.objects.create(
            intern=self.intern,
            from_date=date(2026, 3, 23),
            to_date=date(2026, 3, 24),
            business_days=2,
            type=LeaveRequest.LeaveTypeChoices.OTHER,
            reason="Personal errand",
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("leave-deny", kwargs={"pk": leave.id}),
            {"admin_note": "Insufficient coverage."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], LeaveRequest.StatusChoices.DENIED)
        self.assertEqual(response.data["admin_note"], "Insufficient coverage.")

    def test_admin_cannot_submit_leave(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("leave-list"),
            {
                "from_date": "2026-03-23",
                "to_date": "2026-03-24",
                "type": "vacation",
                "reason": "Trip",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_intern_cannot_approve_leave(self):
        leave = LeaveRequest.objects.create(
            intern=self.other_intern,
            from_date=date(2026, 3, 23),
            to_date=date(2026, 3, 24),
            business_days=2,
            type=LeaveRequest.LeaveTypeChoices.VACATION,
            reason="Trip",
        )
        self.client.force_authenticate(user=self.intern)

        response = self.client.post(reverse("leave-approve", kwargs={"pk": leave.id}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
