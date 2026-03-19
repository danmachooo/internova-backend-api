from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.assets.models import Laptop, LaptopIssueReport
from apps.interns.models import InternProfile
from datetime import date


class AssetViewTests(APITestCase):
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
        self.laptop = Laptop.objects.create(
            brand="Lenovo ThinkPad",
            serial_no="SN-001",
            assigned_to=self.intern,
            status=Laptop.StatusChoices.ASSIGNED,
        )

    def test_admin_can_create_laptop(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("laptop-list"),
            {
                "brand": "Dell Latitude",
                "serial_no": "SN-002",
                "status": "available",
                "accounts": "intern2",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Laptop.objects.count(), 2)

    def test_intern_can_submit_issue_report(self):
        self.client.force_authenticate(user=self.intern)

        response = self.client.post(
            reverse("laptop-issue-list"),
            {"laptop": str(self.laptop.id), "description": "Battery issue"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], LaptopIssueReport.StatusChoices.OPEN)

    def test_admin_can_resolve_issue_report(self):
        report = LaptopIssueReport.objects.create(
            intern=self.intern,
            laptop=self.laptop,
            description="Battery issue",
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse("laptop-issue-detail", kwargs={"pk": report.id}),
            {"status": "resolved", "admin_note": "Battery replaced"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], LaptopIssueReport.StatusChoices.RESOLVED)

    def test_intern_sees_own_issue_only(self):
        own_report = LaptopIssueReport.objects.create(
            intern=self.intern,
            laptop=self.laptop,
            description="Battery issue",
        )
        other_laptop = Laptop.objects.create(
            brand="MacBook Pro",
            serial_no="SN-003",
            assigned_to=self.other_intern,
            status=Laptop.StatusChoices.ASSIGNED,
        )
        LaptopIssueReport.objects.create(
            intern=self.other_intern,
            laptop=other_laptop,
            description="Screen flicker",
        )
        self.client.force_authenticate(user=self.intern)

        response = self.client.get(reverse("laptop-issue-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(own_report.id))
