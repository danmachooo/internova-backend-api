from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from common.models import BaseModel


def dar_upload_to(instance, filename):
    return f"dar/{instance.intern_id}/{instance.date}_{filename}"


class DailyActivityReport(BaseModel):
    class StatusChoices(models.TextChoices):
        SUBMITTED = "submitted", _("Submitted")
        MISSING = "missing", _("Missing")

    intern = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="daily_activity_reports",
    )
    date = models.DateField()
    file = models.FileField(upload_to=dar_upload_to, null=True, blank=True)
    upload_time = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.MISSING,
    )

    def __str__(self):
        return f"{self.intern.email} - {self.date}"

    class Meta:
        db_table = "dar_dailyactivityreport"
        ordering = ["-date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["intern", "date"],
                name="dar_unique_intern_date",
            )
        ]
        indexes = [
            models.Index(fields=["intern"], name="dar_intern_idx"),
            models.Index(fields=["date"], name="dar_date_idx"),
            models.Index(fields=["status"], name="dar_status_idx"),
        ]
