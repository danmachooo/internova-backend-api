from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.accounts.models import User
from common.models import BaseModel


class Assessment(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(default="", blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_assessments",
    )

    def publish(self):
        self.is_published = True
        if self.published_at is None:
            self.published_at = timezone.now()
            self.save(update_fields=["is_published", "published_at", "updated_at"])
        else:
            self.save(update_fields=["is_published", "updated_at"])
        return self

    def unpublish(self):
        self.is_published = False
        self.save(update_fields=["is_published", "updated_at"])
        return self

    def __str__(self):
        return self.title

    class Meta:
        db_table = "assessments_assessment"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_published"], name="assessment_published_idx"),
        ]


class AssessmentPage(BaseModel):
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="pages",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.assessment.title} - {self.title}"

    class Meta:
        db_table = "assessments_assessmentpage"
        ordering = ["order", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["assessment", "order"],
                name="assessments_page_unique_assessment_order",
            )
        ]
        indexes = [
            models.Index(fields=["assessment"], name="assessment_page_assessment_idx"),
            models.Index(fields=["assessment", "order"], name="assessment_page_order_idx"),
        ]


class AssessmentQuestion(BaseModel):
    page = models.ForeignKey(
        AssessmentPage,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    prompt = models.TextField()
    choices = models.JSONField()
    correct_index = models.IntegerField()
    order = models.IntegerField(default=0)

    def clean(self):
        super().clean()
        if not isinstance(self.choices, list) or len(self.choices) < 2:
            raise ValidationError({"choices": ["Choices must contain at least 2 items."]})
        if any(not isinstance(choice, str) or not choice.strip() for choice in self.choices):
            raise ValidationError({"choices": ["Each choice must be a non-empty string."]})
        if self.correct_index < 0 or self.correct_index >= len(self.choices):
            raise ValidationError(
                {"correct_index": ["Correct index must point to a valid choice."]}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.prompt[:50]

    class Meta:
        db_table = "assessments_assessmentquestion"
        ordering = ["order", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["page", "order"],
                name="assessments_question_unique_page_order",
            )
        ]
        indexes = [
            models.Index(fields=["page"], name="assessment_question_page_idx"),
        ]


class InternAttempt(BaseModel):
    intern = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assessment_attempts",
    )
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.intern.email} - {self.assessment.title}"

    class Meta:
        db_table = "assessments_internattempt"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["intern", "assessment"],
                name="assessments_attempt_unique_intern_assessment",
            )
        ]
        indexes = [
            models.Index(fields=["intern"], name="attempt_intern_idx"),
            models.Index(fields=["assessment"], name="attempt_assessment_idx"),
            models.Index(fields=["completed"], name="attempt_completed_idx"),
        ]
