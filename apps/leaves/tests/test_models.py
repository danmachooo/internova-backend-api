from datetime import date

from django.test import TestCase

from apps.accounts.models import User
from apps.leaves.models import LeaveRequest


class LeaveRequestModelTests(TestCase):
    def setUp(self):
        self.intern = User.objects.create_user(
            email="intern@example.com",
            name="Intern User",
            password="StrongPass123!",
            role=User.RoleChoices.INTERN,
        )

    def test_leave_request_defaults_pending_status(self):
        leave = LeaveRequest.objects.create(
            intern=self.intern,
            from_date=date(2026, 3, 23),
            to_date=date(2026, 3, 24),
            type=LeaveRequest.LeaveTypeChoices.SICK,
            reason="Flu symptoms",
        )

        self.assertEqual(leave.status, LeaveRequest.StatusChoices.PENDING)
        self.assertEqual(leave.business_days, 0)
