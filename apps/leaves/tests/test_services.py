from datetime import date

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.calendar.models import CalendarSettings
from apps.leaves.models import LeaveRequest
from apps.leaves.services import LeaveService


class LeaveServiceTests(TestCase):
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

    def test_submit_computes_business_days(self):
        leave = LeaveService.submit(
            intern=self.intern,
            validated_data={
                "from_date": date(2026, 3, 23),
                "to_date": date(2026, 3, 24),
                "type": LeaveRequest.LeaveTypeChoices.SICK,
                "reason": "Medical appointment",
            },
        )

        self.assertEqual(leave.business_days, 2)
        self.assertEqual(leave.status, LeaveRequest.StatusChoices.PENDING)

    def test_approve_updates_leave_status(self):
        leave = LeaveRequest.objects.create(
            intern=self.intern,
            from_date=date(2026, 3, 23),
            to_date=date(2026, 3, 24),
            business_days=2,
            type=LeaveRequest.LeaveTypeChoices.VACATION,
            reason="Family trip",
        )

        updated_leave = LeaveService.approve(
            leave=leave,
            decided_by=self.admin,
            admin_note="Approved.",
        )

        self.assertEqual(updated_leave.status, LeaveRequest.StatusChoices.APPROVED)
        self.assertEqual(updated_leave.decided_by, self.admin)
        self.assertEqual(updated_leave.admin_note, "Approved.")

    def test_deny_non_pending_leave_raises_validation_error(self):
        leave = LeaveRequest.objects.create(
            intern=self.intern,
            from_date=date(2026, 3, 23),
            to_date=date(2026, 3, 24),
            business_days=2,
            type=LeaveRequest.LeaveTypeChoices.OTHER,
            reason="Personal matter",
            status=LeaveRequest.StatusChoices.DENIED,
        )

        with self.assertRaises(ValidationError):
            LeaveService.deny(
                leave=leave,
                decided_by=self.admin,
                admin_note="Already denied.",
            )
