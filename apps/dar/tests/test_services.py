from datetime import date
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.dar.models import DailyActivityReport
from apps.dar.services import DailyActivityReportService


class DailyActivityReportServiceTests(TestCase):
    def setUp(self):
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
        self.inactive_intern = User.objects.create_user(
            email="inactive@example.com",
            name="Inactive Intern",
            password="StrongPass123!",
            role=User.RoleChoices.INTERN,
            status=User.StatusChoices.INACTIVE,
        )

    @patch("apps.dar.services.timezone.localtime")
    def test_submit_report_sets_submitted_status_and_upload_time(self, mock_localtime):
        mock_localtime.return_value = timezone.make_aware(
            timezone.datetime(2026, 3, 24, 9, 15)
        )
        upload = SimpleUploadedFile(
            "report.pdf",
            b"%PDF-1.4 test data",
            content_type="application/pdf",
        )

        report = DailyActivityReportService.submit_report(
            intern=self.intern,
            validated_data={"date": date(2026, 3, 24), "file": upload},
        )

        self.assertEqual(report.status, DailyActivityReport.StatusChoices.SUBMITTED)
        self.assertEqual(report.upload_time.isoformat(), "09:15:00")

    def test_submit_report_duplicate_date_raises_validation_error(self):
        DailyActivityReport.objects.create(
            intern=self.intern,
            date=date(2026, 3, 24),
            status=DailyActivityReport.StatusChoices.SUBMITTED,
        )
        upload = SimpleUploadedFile(
            "report.pdf",
            b"%PDF-1.4 test data",
            content_type="application/pdf",
        )

        with self.assertRaises(ValidationError):
            DailyActivityReportService.submit_report(
                intern=self.intern,
                validated_data={"date": date(2026, 3, 24), "file": upload},
            )

    def test_missing_reports_returns_active_interns_without_submissions(self):
        DailyActivityReport.objects.create(
            intern=self.intern,
            date=date(2026, 3, 24),
            status=DailyActivityReport.StatusChoices.SUBMITTED,
        )

        interns = DailyActivityReportService.missing_reports(report_date=date(2026, 3, 24))

        self.assertEqual(list(interns.order_by("email")), [self.other_intern])
