from django.contrib.auth.hashers import identify_hasher, make_password
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.batches.models import Batch
from common.models import BaseModel


def avatar_upload_to(instance, filename):
    extension = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    return f"avatars/{instance.user_id}.{extension}"


class InternProfileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("user", "batch")

    def active(self):
        return self.get_queryset().filter(user__status=User.StatusChoices.ACTIVE)

    def in_batch(self, batch_id):
        return self.get_queryset().filter(batch_id=batch_id)

    def awaiting_role_assignment(self):
        return self.get_queryset().filter(intern_role__isnull=True)


class InternProfile(BaseModel):
    class InternRoleChoices(models.TextChoices):
        DEVELOPER = "Developer", _("Developer")
        QUALITY_ASSURANCE = "Quality Assurance", _("Quality Assurance")
        PROJECT_MANAGER = "Project Manager", _("Project Manager")
        BUSINESS_ANALYST = "Business Analyst", _("Business Analyst")

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="intern_profile",
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="intern_profiles",
    )
    school = models.CharField(max_length=255)
    intern_role = models.CharField(
        max_length=50,
        choices=InternRoleChoices.choices,
        null=True,
        blank=True,
    )
    phone = models.CharField(max_length=20)
    github_username = models.CharField(max_length=100, null=True, blank=True)
    required_hours = models.DecimalField(max_digits=6, decimal_places=2, default=480.00)
    rendered_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    start_date = models.DateField()
    birthdate = models.DateField()
    avatar = models.ImageField(upload_to=avatar_upload_to, null=True, blank=True)
    company_account_email = models.EmailField(null=True, blank=True)
    company_account_password = models.CharField(max_length=255, null=True, blank=True)
    assessment_required = models.BooleanField(default=True)
    assessment_completed_at = models.DateTimeField(null=True, blank=True)
    assessment_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    objects = InternProfileManager()

    @property
    def name(self):
        return self.user.name

    @property
    def email(self):
        return self.user.email

    @property
    def status(self):
        return self.user.status

    def __str__(self):
        return self.user.name

    class Meta:
        db_table = "interns_internprofile"
        ordering = ["user__name"]
        indexes = [
            models.Index(fields=["user"], name="interns_profile_user_idx"),
            models.Index(fields=["batch"], name="interns_profile_batch_idx"),
            models.Index(fields=["intern_role"], name="interns_profile_role_idx"),
        ]


class InternRegistrationRequest(BaseModel):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", _("Pending")
        APPROVED = "approved", _("Approved")
        DENIED = "denied", _("Denied")

    name = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(max_length=128)
    github_username = models.CharField(max_length=100, null=True, blank=True)
    school = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    birthdate = models.DateField()
    start_date = models.DateField()
    required_hours = models.IntegerField(default=480)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    intern = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registration_requests",
    )

    def save(self, *args, **kwargs):
        try:
            identify_hasher(self.password)
        except Exception:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    class Meta:
        db_table = "interns_internregistrationrequest"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"], name="interns_reg_status_idx"),
            models.Index(fields=["email"], name="interns_reg_email_idx"),
        ]
