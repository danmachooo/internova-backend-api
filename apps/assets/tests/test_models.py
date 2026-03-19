from django.test import TestCase

from apps.assets.models import Laptop, LaptopIssueReport


class AssetModelTests(TestCase):
    def test_laptop_defaults_available_status(self):
        laptop = Laptop.objects.create(
            brand="Lenovo ThinkPad",
            serial_no="SN-001",
        )

        self.assertEqual(laptop.status, Laptop.StatusChoices.AVAILABLE)

    def test_issue_report_defaults_open_status(self):
        self.assertEqual(LaptopIssueReport.StatusChoices.OPEN, "open")
