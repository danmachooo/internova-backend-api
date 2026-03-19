from datetime import date
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.batches.models import Batch
from apps.interns.models import InternProfile, InternRegistrationRequest


class InternsViewTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com",
            name="Admin User",
            password="StrongPass123!",
            role=User.RoleChoices.STAFFADMIN,
        )
        self.intern_user = User.objects.create_user(
            email="intern@example.com",
            name="Intern User",
            password="StrongPass123!",
            role=User.RoleChoices.INTERN,
        )
        self.batch = Batch.objects.create(
            name="Batch 2026-A",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 6, 1),
        )
        self.profile = InternProfile.objects.create(
            user=self.intern_user,
            batch=self.batch,
            school="Test School",
            phone="09171234567",
            github_username="intern-gh",
            required_hours=Decimal("480.00"),
            rendered_hours=Decimal("120.50"),
            start_date=date(2026, 3, 1),
            birthdate=date(2000, 1, 1),
        )
        self.registration = InternRegistrationRequest.objects.create(
            name="Applicant",
            email="applicant@example.com",
            password="StrongPass123!",
            school="Test School",
            phone="09171234567",
            birthdate=date(2000, 1, 1),
            start_date=date(2026, 3, 1),
        )

    def test_registration_flow(self):
        response = self.client.post(
            reverse("registration-list"),
            {
                "name": "New Applicant",
                "email": "newapplicant@example.com",
                "password": "StrongPass123!",
                "school": "Another School",
                "phone": "09991234567",
                "birthdate": "2001-01-01",
                "start_date": "2026-04-01",
                "required_hours": 480,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], InternRegistrationRequest.StatusChoices.PENDING)

    def test_registration_rejects_existing_user_email(self):
        response = self.client.post(
            reverse("registration-list"),
            {
                "name": "Existing User Applicant",
                "email": self.intern_user.email,
                "password": "StrongPass123!",
                "school": "Another School",
                "phone": "09991234567",
                "birthdate": "2001-01-01",
                "start_date": "2026-04-01",
                "required_hours": 480,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["errors"]["email"], ["A user with this email already exists."])

    def test_approval_creates_profile(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(reverse("registration-approve", args=[self.registration.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.status, InternRegistrationRequest.StatusChoices.APPROVED)
        self.assertTrue(InternProfile.objects.filter(user=self.registration.intern).exists())

    def test_denial_marks_registration_denied(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(reverse("registration-deny", args=[self.registration.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.status, InternRegistrationRequest.StatusChoices.DENIED)

    def test_permission_checks_block_intern_from_admin_registration_actions(self):
        self.client.force_authenticate(user=self.intern_user)

        response = self.client.get(reverse("registration-list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_hours_breakdown(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse("intern-hours-breakdown"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["email"], self.intern_user.email)

    def test_admin_can_view_intern_attempts_fallback(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse("intern-attempts", args=[self.profile.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_intern_can_only_retrieve_self(self):
        self.client.force_authenticate(user=self.intern_user)

        response = self.client.get(reverse("intern-detail", args=[self.profile.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.intern_user.email)

    def test_approval_rejects_duplicate_existing_user_email(self):
        duplicate_registration = InternRegistrationRequest.objects.create(
            name="Duplicate Applicant",
            email=self.intern_user.email,
            password="StrongPass123!",
            school="Test School",
            phone="09171234567",
            birthdate=date(2000, 1, 1),
            start_date=date(2026, 3, 1),
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(reverse("registration-approve", args=[duplicate_registration.id]))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["errors"]["email"], ["A user with this email already exists."])
