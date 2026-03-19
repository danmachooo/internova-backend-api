from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.projects.models import Project


class ProjectService:
    @staticmethod
    def assign_intern(*, project, intern_id):
        intern = get_object_or_404(
            User.objects.filter(role=User.RoleChoices.INTERN),
            pk=intern_id,
        )
        project.assigned_interns.add(intern)
        return project

    @staticmethod
    def unassign_intern(*, project, intern_id):
        intern = get_object_or_404(
            User.objects.filter(role=User.RoleChoices.INTERN),
            pk=intern_id,
        )
        if not project.assigned_interns.filter(pk=intern.pk).exists():
            raise ValidationError("This intern is not assigned to the project.")
        project.assigned_interns.remove(intern)
        return project
