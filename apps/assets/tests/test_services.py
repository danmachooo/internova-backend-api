from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.assets.models import Laptop, LaptopIssueReport
from apps.assets.services import LaptopIssueReportService, LaptopService


class AssetServiceTests(TestCase):
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
        self.laptop = Laptop.objects.create(
            brand="Lenovo ThinkPad",
            serial_no="SN-001",
            assigned_to=self.intern,
            status=Laptop.StatusChoices.ASSIGNED,
        )

    def test_update_laptop_syncs_assigned_status(self):
        updated = LaptopService.update_laptop(
            laptop=self.laptop,
            validated_data={"assigned_to": None},
        )

        self.assertEqual(updated.status, Laptop.StatusChoices.AVAILABLE)

    def test_submit_issue_requires_assigned_laptop(self):
        with self.assertRaises(ValidationError):
            LaptopIssueReportService.submit_report(
                intern=self.other_intern,
                validated_data={"laptop": self.laptop, "description": "Broken keyboard"},
            )

    def test_update_report_sets_resolution_fields(self):
        report = LaptopIssueReport.objects.create(
            intern=self.intern,
            laptop=self.laptop,
            description="Broken keyboard",
        )

        report = LaptopIssueReportService.update_report(
            report=report,
            validated_data={"status": LaptopIssueReport.StatusChoices.RESOLVED, "admin_note": "Replaced keyboard"},
            resolved_by=self.admin,
        )

        self.assertEqual(report.status, LaptopIssueReport.StatusChoices.RESOLVED)
        self.assertEqual(report.resolved_by, self.admin)
        self.assertIsNotNone(report.resolved_at)
