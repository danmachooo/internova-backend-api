from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.feature_access.models import FeatureAccessConfig


class FeatureAccessViewTests(APITestCase):
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
        self.config = FeatureAccessConfig.get()

    def test_superadmin_can_get_feature_access_config(self):
        self.client.force_authenticate(user=self.superadmin)

        response = self.client.get(reverse("feature-access"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)
        self.assertIn("admin_features", response.data)
        self.assertIn("intern_features", response.data)

    def test_superadmin_can_update_feature_access_toggle(self):
        self.client.force_authenticate(user=self.superadmin)

        response = self.client.patch(
            reverse("feature-access"),
            {
                "admin_features": {
                    "dashboard": True,
                    "batches": False,
                    "interns": True,
                    "dar": True,
                    "assessments": True,
                    "projects": True,
                    "laptops": True,
                    "calendar": True,
                    "leaves": True,
                    "notifications": True,
                    "profile": True,
                    "adminManagement": True,
                    "featureAccess": False,
                }
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["admin_features"]["batches"])
        self.assertTrue(response.data["admin_features"]["adminManagement"])

    def test_always_on_features_remain_enabled_after_patch(self):
        self.client.force_authenticate(user=self.superadmin)

        response = self.client.patch(
            reverse("feature-access"),
            {
                "admin_features": {
                    "dashboard": False,
                    "batches": True,
                    "interns": True,
                    "dar": True,
                    "assessments": True,
                    "projects": True,
                    "laptops": True,
                    "calendar": True,
                    "leaves": False,
                    "notifications": False,
                    "profile": False,
                    "adminManagement": False,
                    "featureAccess": False,
                },
                "intern_features": {
                    "dashboard": False,
                    "attendance": True,
                    "leave": False,
                    "dar": True,
                    "laptopIssue": True,
                    "notifications": False,
                    "profile": False,
                    "extra": True
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        valid_response = self.client.patch(
            reverse("feature-access"),
            {
                "admin_features": {
                    "dashboard": False,
                    "batches": True,
                    "interns": True,
                    "dar": True,
                    "assessments": True,
                    "projects": True,
                    "laptops": True,
                    "calendar": True,
                    "leaves": False,
                    "notifications": False,
                    "profile": False,
                    "adminManagement": False,
                    "featureAccess": False,
                },
                "intern_features": {
                    "dashboard": False,
                    "attendance": True,
                    "leave": False,
                    "dar": True,
                    "laptopIssue": True,
                    "notifications": False,
                    "profile": False,
                },
            },
            format="json",
        )

        self.assertEqual(valid_response.status_code, status.HTTP_200_OK)
        self.assertTrue(valid_response.data["admin_features"]["dashboard"])
        self.assertTrue(valid_response.data["admin_features"]["leaves"])
        self.assertTrue(valid_response.data["admin_features"]["notifications"])
        self.assertTrue(valid_response.data["admin_features"]["profile"])
        self.assertTrue(valid_response.data["intern_features"]["dashboard"])
        self.assertTrue(valid_response.data["intern_features"]["notifications"])
        self.assertTrue(valid_response.data["intern_features"]["profile"])
        self.assertFalse(valid_response.data["intern_features"]["leave"])

    def test_staffadmin_is_rejected(self):
        self.client.force_authenticate(user=self.staffadmin)

        response = self.client.get(reverse("feature-access"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
