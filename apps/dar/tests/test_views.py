from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.dar.models import DailyActivityReport
from apps.interns.models import InternProfile


class DailyActivityReportViewTests(APITestCase):
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

    def test_upload_success_returns_201(self):
        self.client.force_authenticate(user=self.intern)
        upload = SimpleUploadedFile(
            "report.pdf",
            b"%PDF-1.4 test data",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("dar-list"),
            {"date": "2026-03-24", "file": upload},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], DailyActivityReport.StatusChoices.SUBMITTED)
        self.assertEqual(DailyActivityReport.objects.count(), 1)

    def test_wrong_file_type_rejected(self):
        self.client.force_authenticate(user=self.intern)
        upload = SimpleUploadedFile(
            "report.txt",
            b"plain text",
            content_type="text/plain",
        )

        response = self.client.post(
            reverse("dar-list"),
            {"date": "2026-03-24", "file": upload},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["errors"]["file"][0], "Only PDF files are accepted.")

    def test_oversized_file_rejected(self):
        self.client.force_authenticate(user=self.intern)
        upload = SimpleUploadedFile(
            "report.pdf",
            b"0" * (10 * 1024 * 1024 + 1),
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("dar-list"),
            {"date": "2026-03-24", "file": upload},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["errors"]["file"][0],
            "File size cannot exceed 10MB.",
        )

    def test_missing_report_detection_returns_active_interns_without_submission(self):
        DailyActivityReport.objects.create(
            intern=self.intern,
            date=date(2026, 3, 24),
            status=DailyActivityReport.StatusChoices.SUBMITTED,
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            reverse("dar-missing"),
            {"date": "2026-03-24"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["intern_id"], str(self.other_intern.id))

    def test_admin_cannot_upload_dar(self):
        self.client.force_authenticate(user=self.admin)
        upload = SimpleUploadedFile(
            "report.pdf",
            b"%PDF-1.4 test data",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("dar-list"),
            {"date": "2026-03-24", "file": upload},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
