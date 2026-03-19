from django.test import TestCase

from apps.accounts.models import User
from apps.accounts.services import AdminUserService, AuthService


class AuthServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="intern@example.com",
            name="Intern User",
            password="StrongPass123!",
            role=User.RoleChoices.INTERN,
        )

    def test_login_updates_last_login_at(self):
        payload = AuthService.login(
            email="intern@example.com",
            password="StrongPass123!",
        )

        self.user.refresh_from_db()
        self.assertIn("access", payload)
        self.assertIn("refresh", payload)
        self.assertIsNotNone(self.user.last_login_at)


class AdminUserServiceTests(TestCase):
    def test_create_admin_hashes_password_and_sets_staff_flags(self):
        user = AdminUserService.create_admin(
            validated_data={
                "email": "staffadmin@example.com",
                "name": "Staff Admin",
                "password": "StrongPass123!",
                "role": User.RoleChoices.STAFFADMIN,
                "status": User.StatusChoices.ACTIVE,
            }
        )

        self.assertNotEqual(user.password, "StrongPass123!")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertTrue(user.is_staff)
