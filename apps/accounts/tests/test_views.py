from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User


class AccountsViewTests(APITestCase):
    def setUp(self):
        self.superadmin = User.objects.create_user(
            email="superadmin@example.com",
            name="Super Admin",
            password="StrongPass123!",
            role=User.RoleChoices.SUPERADMIN,
        )
        self.staffadmin = User.objects.create_user(
            email="staffadmin@example.com",
            name="Staff Admin",
            password="StrongPass123!",
            role=User.RoleChoices.STAFFADMIN,
        )
        self.intern = User.objects.create_user(
            email="intern@example.com",
            name="Intern User",
            password="StrongPass123!",
            role=User.RoleChoices.INTERN,
        )

        self.login_url = reverse("auth-login")
        self.logout_url = reverse("auth-logout")
        self.refresh_url = reverse("auth-refresh")
        self.me_url = reverse("auth-me")
        self.change_password_url = reverse("auth-change-password")
        self.admins_url = reverse("admin-user-list")

    def test_login_success(self):
        response = self.client.post(
            self.login_url,
            {"email": "intern@example.com", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "intern@example.com")

    def test_login_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            {"email": "intern@example.com", "password": "WrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid email or password.")

    def test_login_inactive_account(self):
        self.intern.status = User.StatusChoices.INACTIVE
        self.intern.save(update_fields=["status", "updated_at", "is_active", "is_staff"])

        response = self.client.post(
            self.login_url,
            {"email": "intern@example.com", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "This account is inactive.")

    def test_logout_blacklists_token(self):
        refresh = RefreshToken.for_user(self.intern)
        self.client.force_authenticate(user=self.intern)

        response = self.client.post(
            self.logout_url,
            {"refresh": str(refresh)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": str(refresh)},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_own_profile(self):
        self.client.force_authenticate(user=self.intern)

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "intern@example.com")
        self.assertNotIn("password", response.data)

    def test_me_rejects_duplicate_email(self):
        self.client.force_authenticate(user=self.intern)

        response = self.client.patch(
            self.me_url,
            {"email": self.staffadmin.email},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["errors"]["email"], ["A user with this email already exists."])

    def test_change_password_success(self):
        self.client.force_authenticate(user=self.intern)

        response = self.client.post(
            self.change_password_url,
            {
                "old_password": "StrongPass123!",
                "new_password": "NewStrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.intern.refresh_from_db()
        self.assertTrue(self.intern.check_password("NewStrongPass123!"))

    def test_admin_crud_superadmin_only(self):
        self.client.force_authenticate(user=self.superadmin)
        create_response = self.client.post(
            self.admins_url,
            {
                "email": "newstaff@example.com",
                "name": "New Staff",
                "password": "StrongPass123!",
                "role": User.RoleChoices.STAFFADMIN,
                "status": User.StatusChoices.ACTIVE,
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=self.staffadmin)
        forbidden_response = self.client.get(self.admins_url)

        self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_create_rejects_duplicate_email(self):
        self.client.force_authenticate(user=self.superadmin)

        response = self.client.post(
            self.admins_url,
            {
                "email": self.staffadmin.email,
                "name": "Duplicate Staff",
                "password": "StrongPass123!",
                "role": User.RoleChoices.STAFFADMIN,
                "status": User.StatusChoices.ACTIVE,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["errors"]["email"], ["A user with this email already exists."])
