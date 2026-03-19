from datetime import date

from django.test import TestCase

from apps.accounts.models import User
from apps.attendance.models import AttendanceRecord


class AttendanceRecordModelTests(TestCase):
    def setUp(self):
        self.intern = User.objects.create_user(
            email="intern@example.com",
            name="Intern User",
            password="StrongPass123!",
            role=User.RoleChoices.INTERN,
        )

    def test_attendance_record_defaults_hours_and_status(self):
        record = AttendanceRecord.objects.create(
            intern=self.intern,
            date=date(2026, 3, 23),
            status=AttendanceRecord.StatusChoices.ABSENT,
        )

        self.assertEqual(str(record.hours), "0.00")
        self.assertEqual(record.status, AttendanceRecord.StatusChoices.ABSENT)
