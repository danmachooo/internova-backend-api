from datetime import date

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.projects.models import Project
from apps.projects.services import ProjectService


class ProjectServiceTests(TestCase):
    def setUp(self):
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

    def test_assign_intern_adds_intern_to_project(self):
        ProjectService.assign_intern(project=self.project, intern_id=self.intern.id)

        self.assertTrue(self.project.assigned_interns.filter(pk=self.intern.pk).exists())

    def test_unassign_intern_requires_existing_assignment(self):
        with self.assertRaises(ValidationError):
            ProjectService.unassign_intern(project=self.project, intern_id=self.intern.id)
