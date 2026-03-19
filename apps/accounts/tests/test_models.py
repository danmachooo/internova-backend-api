from django.test import TestCase

from apps.accounts.models import User


class UserModelTests(TestCase):
    def test_create_superuser_sets_admin_flags(self):
        user = User.objects.create_superuser(
            email="superadmin@example.com",
            name="Super Admin",
            password="StrongPass123!",
        )

        self.assertEqual(user.role, User.RoleChoices.SUPERADMIN)
        self.assertEqual(user.status, User.StatusChoices.ACTIVE)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)

    def test_save_inactive_status_sets_is_active_false(self):
        user = User.objects.create_user(
            email="staffadmin@example.com",
            name="Staff Admin",
            password="StrongPass123!",
            role=User.RoleChoices.STAFFADMIN,
        )

        user.status = User.StatusChoices.INACTIVE
        user.save(update_fields=["status", "updated_at", "is_active", "is_staff"])

        user.refresh_from_db()
        self.assertFalse(user.is_active)
