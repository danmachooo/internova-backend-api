from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel


class Batch(BaseModel):
    class StatusChoices(models.TextChoices):
        ACTIVE = "active", _("Active")
        COMPLETED = "completed", _("Completed")

    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
    )
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    def clean(self):
        super().clean()
        if self.end_date < self.start_date:
            from django.core.exceptions import ValidationError

            raise ValidationError({"end_date": ["End date must be on or after start date."]})

    def __str__(self):
        return self.name

    class Meta:
        db_table = "batches_batch"
        ordering = ["-start_date", "-created_at"]
        indexes = [
            models.Index(fields=["status"], name="batches_batch_status_idx"),
        ]
