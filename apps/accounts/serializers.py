from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.accounts.models import User


def validate_unique_user_email(value, instance=None):
    queryset = User.objects.filter(email__iexact=value)
    if instance is not None:
        queryset = queryset.exclude(pk=instance.pk)
    if queryset.exists():
        raise serializers.ValidationError("A user with this email already exists.")
    return value


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name", "email", "role", "status")


class UserDetailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[])
    password = serializers.CharField(write_only=True, required=False, trim_whitespace=False)

    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "email",
            "password",
            "role",
            "status",
            "last_login_at",
            "is_active",
            "is_staff",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "last_login_at",
            "is_active",
            "is_staff",
            "created_at",
            "updated_at",
        )

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_email(self, value):
        user = self.instance if isinstance(self.instance, User) else None
        return validate_unique_user_email(value, instance=user)

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.method == "POST" and not attrs.get("password"):
            raise serializers.ValidationError({"password": ["This field is required."]})
        return attrs


class MeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[])

    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "email",
            "role",
            "status",
            "last_login_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "role",
            "status",
            "last_login_at",
            "created_at",
            "updated_at",
        )

    def validate_email(self, value):
        return validate_unique_user_email(value, instance=self.instance)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(trim_whitespace=False)
    new_password = serializers.CharField(trim_whitespace=False)

    def validate_new_password(self, value):
        validate_password(value, self.context["request"].user)
        return value
