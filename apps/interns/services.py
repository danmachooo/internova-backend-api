from decimal import Decimal

from django.apps import apps
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.accounts.services import ensure_email_available
from apps.accounts.models import User
from apps.interns.models import InternProfile, InternRegistrationRequest


class InternService:
    @staticmethod
    def submit_registration(*, validated_data):
        ensure_email_available(email=validated_data["email"])
        return InternRegistrationRequest.objects.create(**validated_data)

    @staticmethod
    @transaction.atomic
    def approve_registration(registration_id, decided_by):
        registration = get_object_or_404(InternRegistrationRequest, pk=registration_id)
        if registration.status != InternRegistrationRequest.StatusChoices.PENDING:
            raise ValidationError("Only pending registration requests can be approved.")
        ensure_email_available(email=registration.email)

        user = User(
            email=registration.email,
            name=registration.name,
            role=User.RoleChoices.INTERN,
            status=User.StatusChoices.ACTIVE,
        )
        user.password = registration.password
        user.save()

        InternProfile.objects.create(
            user=user,
            school=registration.school,
            phone=registration.phone,
            github_username=registration.github_username,
            required_hours=Decimal(registration.required_hours),
            start_date=registration.start_date,
            birthdate=registration.birthdate,
        )

        registration.status = InternRegistrationRequest.StatusChoices.APPROVED
        registration.decided_at = timezone.now()
        registration.intern = user
        registration.save(update_fields=["status", "decided_at", "intern", "updated_at"])
        return registration

    @staticmethod
    def deny_registration(registration_id, decided_by):
        registration = get_object_or_404(InternRegistrationRequest, pk=registration_id)
        if registration.status != InternRegistrationRequest.StatusChoices.PENDING:
            raise ValidationError("Only pending registration requests can be denied.")

        registration.status = InternRegistrationRequest.StatusChoices.DENIED
        registration.decided_at = timezone.now()
        registration.save(update_fields=["status", "decided_at", "updated_at"])
        return registration

    @staticmethod
    @transaction.atomic
    def create_intern(*, validated_data):
        ensure_email_available(email=validated_data["email"])
        user_data = {
            "email": validated_data.pop("email"),
            "name": validated_data.pop("name"),
            "password": validated_data.pop("password"),
            "role": User.RoleChoices.INTERN,
            "status": validated_data.pop("status", User.StatusChoices.ACTIVE),
        }
        user = User.objects.create_user(**user_data)
        profile = InternProfile.objects.create(user=user, **validated_data)
        return profile

    @staticmethod
    def update_intern(*, profile, validated_data, actor):
        user_updates = {}
        profile_updates = {}

        admin_only_profile_fields = {
            "batch",
            "intern_role",
            "required_hours",
            "rendered_hours",
            "company_account_email",
            "company_account_password",
            "assessment_required",
            "assessment_completed_at",
            "assessment_score",
        }
        admin_only_user_fields = {"status"}

        for field in ("name", "email", "status", "password"):
            if field in validated_data:
                user_updates[field] = validated_data.pop(field)

        for field, value in validated_data.items():
            profile_updates[field] = value

        is_admin = actor.role in User.admin_roles()
        if not is_admin:
            for field in list(user_updates):
                if field in admin_only_user_fields:
                    user_updates.pop(field)
            for field in list(profile_updates):
                if field in admin_only_profile_fields:
                    profile_updates.pop(field)

        if "password" in user_updates:
            profile.user.set_password(user_updates.pop("password"))
            profile.user.save(update_fields=["password", "updated_at"])

        update_user_fields = []
        for field, value in user_updates.items():
            if field == "email":
                ensure_email_available(email=value, exclude_user_id=profile.user_id)
            setattr(profile.user, field, value)
            update_user_fields.append(field)
        if update_user_fields:
            profile.user.save(update_fields=[*update_user_fields, "updated_at", "is_active", "is_staff"])

        update_profile_fields = []
        for field, value in profile_updates.items():
            setattr(profile, field, value)
            update_profile_fields.append(field)
        if update_profile_fields:
            profile.save(update_fields=[*update_profile_fields, "updated_at"])

        return profile

    @staticmethod
    def delete_intern(*, profile):
        profile.user.delete()

    @staticmethod
    def hours_breakdown(*, batch_id=None):
        profiles = InternProfile.objects.active()
        if batch_id:
            profiles = profiles.in_batch(batch_id)

        return [
            {
                "id": profile.id,
                "name": profile.user.name,
                "email": profile.user.email,
                "rendered_hours": str(profile.rendered_hours),
                "required_hours": str(profile.required_hours),
            }
            for profile in profiles.order_by("user__name")
        ]

    @staticmethod
    def list_attempt_summaries(*, intern):
        if not apps.is_installed("apps.assessments"):
            return []

        try:
            intern_attempt_model = apps.get_model("assessments", "InternAttempt")
        except LookupError:
            return []

        attempts = (
            intern_attempt_model.objects.select_related("assessment")
            .filter(intern=intern)
            .order_by("assessment__title")
        )
        return [
            {
                "assessment_id": attempt.assessment_id,
                "assessment_title": attempt.assessment.title,
                "score": str(attempt.score),
                "completed": attempt.completed,
                "completed_at": attempt.completed_at,
                "created_at": attempt.created_at,
            }
            for attempt in attempts
        ]
