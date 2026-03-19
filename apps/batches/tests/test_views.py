from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.batches.models import Batch


class BatchViewSetTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
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
        self.batch = Batch.objects.create(
            name="Batch 2026-A",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 6, 1),
            status=Batch.StatusChoices.ACTIVE,
            progress=25,
        )
        self.completed_batch = Batch.objects.create(
            name="Batch 2025-Z",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 4, 1),
            status=Batch.StatusChoices.COMPLETED,
            progress=100,
        )

    def test_admin_can_crud_batches(self):
        self.client.force_authenticate(user=self.admin)

        create_response = self.client.post(
            reverse("batch-list"),
            {
                "name": "Batch 2026-B",
                "start_date": "2026-07-01",
                "end_date": "2026-10-01",
                "status": Batch.StatusChoices.ACTIVE,
                "progress": 0,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        list_response = self.client.get(reverse("batch-list"))
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(list_response.data["count"], 3)

        patch_response = self.client.patch(
            reverse("batch-detail", args=[self.batch.id]),
            {"progress": 50},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.progress, 50)

        delete_response = self.client.delete(reverse("batch-detail", args=[self.batch.id]))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_filter_batches_by_status(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse("batch-list"), {"status": Batch.StatusChoices.COMPLETED})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.completed_batch.id))

    def test_batch_interns_action_returns_empty_list_until_interns_app_exists(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse("batch-interns", args=[self.batch.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_intern_cannot_access_batch_endpoints(self):
        self.client.force_authenticate(user=self.intern)

        response = self.client.get(reverse("batch-list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
