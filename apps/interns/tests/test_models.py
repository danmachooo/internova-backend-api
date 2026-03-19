from datetime import date

from django.contrib.auth.hashers import check_password
from django.test import TestCase

from apps.accounts.models import User
from apps.interns.models import InternProfile, InternRegistrationRequest


class InternProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="intern@example.com",
            name="Intern User",
            password="StrongPass123!",
            role=User.RoleChoices.INTERN,
        )

    def test_manager_awaiting_role_assignment_filters_null_roles(self):
        profile = InternProfile.objects.create(
            user=self.user,
            school="Test School",
            phone="09171234567",
            start_date=date(2026, 3, 1),
            birthdate=date(2000, 1, 1),
        )

        queryset = InternProfile.objects.awaiting_role_assignment()

        self.assertIn(profile, queryset)


class InternRegistrationRequestModelTests(TestCase):
    def test_save_hashes_password(self):
        registration = InternRegistrationRequest.objects.create(
            name="Applicant",
            email="applicant@example.com",
            password="StrongPass123!",
            school="Test School",
            phone="09171234567",
            birthdate=date(2000, 1, 1),
            start_date=date(2026, 3, 1),
        )

        self.assertNotEqual(registration.password, "StrongPass123!")
        self.assertTrue(check_password("StrongPass123!", registration.password))
