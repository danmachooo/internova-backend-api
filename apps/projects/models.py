from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from common.models import BaseModel


class Project(BaseModel):
    class StatusChoices(models.TextChoices):
        ACTIVE = "active", _("Active")
        ON_HOLD = "on_hold", _("On Hold")
        COMPLETED = "completed", _("Completed")

    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
    )
    start_date = models.DateField()
    end_date = models.DateField()
    assigned_interns = models.ManyToManyField(
        User,
        related_name="projects",
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "projects_project"
        ordering = ["name", "start_date"]
        indexes = [
            models.Index(fields=["status"], name="projects_status_idx"),
        ]
