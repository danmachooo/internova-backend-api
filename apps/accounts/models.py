from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from common.models import BaseModel


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        name,
        password=None,
        role=None,
        status=None,
        **extra_fields,
    ):
        if not email:
            raise ValueError("Users must have an email address.")
        if not name:
            raise ValueError("Users must have a name.")
        if not password:
            raise ValueError("Users must have a password.")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            role=role or User.RoleChoices.INTERN,
            status=status or User.StatusChoices.ACTIVE,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("role", User.RoleChoices.SUPERADMIN)
        extra_fields.setdefault("status", User.StatusChoices.ACTIVE)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("role") != User.RoleChoices.SUPERADMIN:
            raise ValueError("Superuser must have role='superadmin'.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, name, password, **extra_fields)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    class RoleChoices(models.TextChoices):
        SUPERADMIN = "superadmin", "Super Admin"
        STAFFADMIN = "staffadmin", "Staff Admin"
        INTERN = "intern", "Intern"

    class StatusChoices(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    email = models.EmailField(unique=True)
    last_login = None
    name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.INTERN,
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
    )
    last_login_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    @classmethod
    def admin_roles(cls):
        return (
            cls.RoleChoices.SUPERADMIN,
            cls.RoleChoices.STAFFADMIN,
        )

    def save(self, *args, **kwargs):
        self.is_active = self.status == self.StatusChoices.ACTIVE
        self.is_staff = self.role in self.admin_roles()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    class Meta:
        db_table = "accounts_user"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"], name="accounts_user_email_idx"),
            models.Index(fields=["role"], name="accounts_user_role_idx"),
            models.Index(fields=["status"], name="accounts_user_status_idx"),
        ]
