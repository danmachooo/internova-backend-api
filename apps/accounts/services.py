from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from apps.accounts.models import User


def ensure_email_available(*, email, exclude_user_id=None):
    queryset = User.objects.filter(email__iexact=email)
    if exclude_user_id is not None:
        queryset = queryset.exclude(pk=exclude_user_id)
    if queryset.exists():
        raise ValidationError({"email": ["A user with this email already exists."]})


class AuthService:
    @staticmethod
    def login(*, email, password):
        existing_user = User.objects.filter(email__iexact=email).first()
        if (
            existing_user is not None
            and existing_user.check_password(password)
            and (
                not existing_user.is_active
                or existing_user.status != User.StatusChoices.ACTIVE
            )
        ):
            raise ValidationError("This account is inactive.")

        user = authenticate(username=email, password=password)
        if user is None:
            raise ValidationError("Invalid email or password.")

        user.last_login_at = timezone.now()
        user.save(update_fields=["last_login_at", "updated_at"])

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": user,
        }

    @staticmethod
    def logout(*, refresh_token):
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as exc:
            raise ValidationError("Invalid refresh token.") from exc

    @staticmethod
    def update_profile(*, user, validated_data):
        update_fields = []
        for field in ("name", "email"):
            if field in validated_data:
                if field == "email":
                    ensure_email_available(email=validated_data[field], exclude_user_id=user.pk)
                setattr(user, field, validated_data[field])
                update_fields.append(field)

        if update_fields:
            user.save(update_fields=[*update_fields, "updated_at"])

        return user

    @staticmethod
    def change_password(*, user, old_password, new_password):
        if not user.check_password(old_password):
            raise ValidationError({"old_password": ["Old password is incorrect."]})

        validate_password(new_password, user)
        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])
        return user


class AdminUserService:
    @staticmethod
    def create_admin(*, validated_data):
        password = validated_data.pop("password")
        role = validated_data.pop("role", User.RoleChoices.STAFFADMIN)
        if role not in User.admin_roles():
            raise ValidationError({"role": ["Only admin roles can be managed here."]})
        ensure_email_available(email=validated_data["email"])

        return User.objects.create_user(password=password, role=role, **validated_data)

    @staticmethod
    def update_admin(*, user, validated_data):
        password = validated_data.pop("password", None)
        update_fields = []

        for field in ("name", "email", "role", "status"):
            if field in validated_data:
                value = validated_data[field]
                if field == "role" and value not in User.admin_roles():
                    raise ValidationError(
                        {"role": ["Only admin roles can be managed here."]}
                    )
                if field == "email":
                    ensure_email_available(email=value, exclude_user_id=user.pk)
                setattr(user, field, value)
                update_fields.append(field)

        if password:
            validate_password(password, user)
            user.set_password(password)
            update_fields.append("password")

        if update_fields:
            user.save(update_fields=[*update_fields, "updated_at", "is_active", "is_staff"])

        return user
