from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from common.models import BaseModel


class LeaveRequest(BaseModel):
    class LeaveTypeChoices(models.TextChoices):
        SICK = "sick", _("Sick")
        VACATION = "vacation", _("Vacation")
        EMERGENCY = "emergency", _("Emergency")
        OTHER = "other", _("Other")

    class StatusChoices(models.TextChoices):
        PENDING = "pending", _("Pending")
        APPROVED = "approved", _("Approved")
        DENIED = "denied", _("Denied")

    intern = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )
    from_date = models.DateField()
    to_date = models.DateField()
    business_days = models.IntegerField(default=0)
    type = models.CharField(max_length=20, choices=LeaveTypeChoices.choices)
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    admin_note = models.CharField(max_length=500, null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="decided_leave_requests",
    )

    def __str__(self):
        return f"{self.intern.email} ({self.from_date} to {self.to_date})"

    class Meta:
        db_table = "leaves_leaverequest"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["intern"], name="leaves_intern_idx"),
            models.Index(fields=["status"], name="leaves_status_idx"),
            models.Index(fields=["type"], name="leaves_type_idx"),
        ]
