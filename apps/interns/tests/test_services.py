from datetime import date

from django.test import TestCase

from apps.accounts.models import User
from apps.interns.models import InternProfile, InternRegistrationRequest
from apps.interns.services import InternService


class InternServiceTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com",
            name="Admin User",
            password="StrongPass123!",
            role=User.RoleChoices.STAFFADMIN,
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

    def test_approve_registration_creates_user_and_profile(self):
        approved = InternService.approve_registration(self.registration.id, self.admin)

        self.assertEqual(approved.status, InternRegistrationRequest.StatusChoices.APPROVED)
        self.assertTrue(User.objects.filter(email="applicant@example.com").exists())
        self.assertTrue(InternProfile.objects.filter(user=approved.intern).exists())

    def test_deny_registration_marks_request_denied(self):
        denied = InternService.deny_registration(self.registration.id, self.admin)

        self.assertEqual(denied.status, InternRegistrationRequest.StatusChoices.DENIED)
        self.assertIsNotNone(denied.decided_at)
