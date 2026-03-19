from decimal import Decimal
from datetime import time

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from common.models import BaseModel


class AttendanceRecord(BaseModel):
    class StatusChoices(models.TextChoices):
        PRESENT = "present", _("Present")
        LATE = "late", _("Late")
        ABSENT = "absent", _("Absent")
        OVERTIME = "overtime", _("Overtime")
        UNDERTIME = "undertime", _("Undertime")

    intern = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    date = models.DateField()
    login_time = models.TimeField(null=True, blank=True)
    logout_time = models.TimeField(null=True, blank=True)
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=StatusChoices.choices)

    def __str__(self):
        return f"{self.intern.email} - {self.date}"

    class Meta:
        db_table = "attendance_attendancerecord"
        ordering = ["-date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["intern", "date"],
                name="attendance_unique_intern_date",
            )
        ]
        indexes = [
            models.Index(fields=["intern"], name="attendance_intern_idx"),
            models.Index(fields=["date"], name="attendance_date_idx"),
            models.Index(fields=["status"], name="attendance_status_idx"),
            models.Index(fields=["intern", "date"], name="attendance_intern_date_idx"),
        ]
