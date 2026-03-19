from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from common.models import BaseModel


class Laptop(BaseModel):
    class StatusChoices(models.TextChoices):
        ASSIGNED = "assigned", _("Assigned")
        AVAILABLE = "available", _("Available")
        ISSUED = "issued", _("Issued")

    brand = models.CharField(max_length=100)
    serial_no = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_laptops",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.AVAILABLE,
    )
    accounts = models.CharField(max_length=100, default="")

    def __str__(self):
        return self.serial_no

    class Meta:
        db_table = "assets_laptop"
        ordering = ["brand", "serial_no"]
        indexes = [
            models.Index(fields=["status"], name="assets_laptop_status_idx"),
            models.Index(fields=["assigned_to"], name="assets_laptop_assigned_idx"),
        ]


class LaptopIssueReport(BaseModel):
    class StatusChoices(models.TextChoices):
        OPEN = "open", _("Open")
        IN_PROGRESS = "in_progress", _("In Progress")
        RESOLVED = "resolved", _("Resolved")

    intern = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="laptop_issue_reports",
    )
    laptop = models.ForeignKey(
        Laptop,
        on_delete=models.CASCADE,
        related_name="issue_reports",
    )
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.OPEN,
    )
    admin_note = models.CharField(max_length=500, null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_laptop_issue_reports",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.intern.email} - {self.laptop.serial_no}"

    class Meta:
        db_table = "assets_laptopissuereport"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["intern"], name="laptop_issue_intern_idx"),
            models.Index(fields=["laptop"], name="laptop_issue_laptop_idx"),
            models.Index(fields=["status"], name="laptop_issue_status_idx"),
        ]
