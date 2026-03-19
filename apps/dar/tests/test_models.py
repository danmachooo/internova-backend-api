from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.accounts.models import User
from apps.dar.models import DailyActivityReport, dar_upload_to


class DailyActivityReportModelTests(TestCase):
    def setUp(self):
        self.intern = User.objects.create_user(
            email="intern@example.com",
            name="Intern User",
            password="StrongPass123!",
            role=User.RoleChoices.INTERN,
        )

    def test_daily_activity_report_defaults_to_missing(self):
        report = DailyActivityReport.objects.create(
            intern=self.intern,
            date=date(2026, 3, 24),
        )

        self.assertEqual(report.status, DailyActivityReport.StatusChoices.MISSING)
        self.assertIsNone(report.upload_time)

    def test_dar_upload_to_uses_intern_and_date_path(self):
        report = DailyActivityReport(
            intern=self.intern,
            date=date(2026, 3, 24),
        )
        upload = SimpleUploadedFile(
            "report.pdf",
            b"%PDF-1.4 test data",
            content_type="application/pdf",
        )

        path = dar_upload_to(report, upload.name)

        self.assertEqual(path, f"dar/{self.intern.id}/2026-03-24_report.pdf")
