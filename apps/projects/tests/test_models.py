from datetime import date

from django.test import TestCase

from apps.projects.models import Project


class ProjectModelTests(TestCase):
    def test_project_defaults_active_status(self):
        project = Project.objects.create(
            name="Intern Portal",
            start_date=date(2026, 3, 24),
            end_date=date(2026, 4, 24),
        )

        self.assertEqual(project.status, Project.StatusChoices.ACTIVE)
        self.assertEqual(project.description, "")
