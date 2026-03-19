from datetime import date, time
from decimal import Decimal

from django.test import TestCase

from apps.accounts.models import User
from apps.attendance.models import AttendanceRecord
from apps.attendance.services import AttendanceService
from apps.interns.models import InternProfile


class AttendanceServiceTests(TestCase):
    def setUp(self):
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

    def test_compute_hours_returns_decimal_hours(self):
        hours = AttendanceService.compute_hours(
            login_time=time(9, 0),
            logout_time=time(17, 30),
        )

        self.assertEqual(hours, Decimal("8.50"))

    def test_classify_returns_overtime_for_late_evening_logout(self):
        status = AttendanceService.classify(
            login_time=time(8, 45),
            logout_time=time(18, 0),
        )

        self.assertEqual(status, AttendanceRecord.StatusChoices.OVERTIME)
