from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.projects.models import Project


class ProjectViewTests(APITestCase):
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
        self.project = Project.objects.create(
            name="Intern Portal",
            start_date=date(2026, 3, 24),
            end_date=date(2026, 4, 24),
        )

    def test_admin_can_create_project(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("project-list"),
            {
                "name": "Operations Dashboard",
                "description": "Internal ops tooling",
                "status": "active",
                "start_date": "2026-03-24",
                "end_date": "2026-04-24",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)

    def test_admin_can_assign_intern(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse("project-assign", kwargs={"pk": self.project.id}),
            {"intern": str(self.intern.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["assigned_interns"]), 1)

    def test_admin_can_remove_intern(self):
        self.project.assigned_interns.add(self.intern)
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                "project-unassign",
                kwargs={"pk": self.project.id, "intern_id": self.intern.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["assigned_interns"], [])

    def test_intern_cannot_modify_projects(self):
        self.client.force_authenticate(user=self.intern)

        response = self.client.post(
            reverse("project-list"),
            {
                "name": "Blocked Project",
                "description": "Should fail",
                "status": "active",
                "start_date": "2026-03-24",
                "end_date": "2026-04-24",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
