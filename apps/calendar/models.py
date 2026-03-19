import json

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel


class SQLiteCompatibleIntegerArrayField(ArrayField):
    def db_type(self, connection):
        if connection.vendor == "sqlite":
            return "text"
        return super().db_type(connection)

    def get_placeholder(self, value, compiler, connection):
        if connection.vendor == "sqlite":
            return "%s"
        return super().get_placeholder(value, compiler, connection)

    def get_db_prep_value(self, value, connection, prepared=False):
        prepared_value = super().get_db_prep_value(value, connection, prepared=prepared)
        if connection.vendor == "sqlite" and isinstance(prepared_value, list):
            return json.dumps(prepared_value)
        return prepared_value

    def from_db_value(self, value, expression, connection):
        if connection.vendor == "sqlite" and isinstance(value, str):
            return json.loads(value)
        return value

    def to_python(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
        return super().to_python(value)


class CalendarEvent(BaseModel):
    class TypeChoices(models.TextChoices):
        MEETING = "meeting", _("Meeting")
        PRESENTATION = "presentation", _("Presentation")

    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    type = models.CharField(max_length=20, choices=TypeChoices.choices)
    description = models.TextField(default="")

    def __str__(self):
        return self.title

    class Meta:
        db_table = "calendar_calendarevent"
        ordering = ["date", "time", "title"]
        indexes = [
            models.Index(fields=["date"], name="calendar_event_date_idx"),
        ]


class Holiday(BaseModel):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "calendar_holiday"
        ordering = ["date", "name"]


class CalendarSettings(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    weekend_days = SQLiteCompatibleIntegerArrayField(
        models.IntegerField(),
        default=list,
    )
    updated_at = models.DateTimeField(auto_now=True)

    DEFAULT_WEEKEND_DAYS = [0, 6]

    def save(self, *args, **kwargs):
        self.pk = 1
        if not self.weekend_days:
            self.weekend_days = list(self.DEFAULT_WEEKEND_DAYS)
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={"weekend_days": list(cls.DEFAULT_WEEKEND_DAYS)},
        )
        return obj

    def __str__(self):
        return "Calendar Settings"

    class Meta:
        db_table = "calendar_calendarsettings"
        ordering = ["id"]
