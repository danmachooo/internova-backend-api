from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.serializers import validate_unique_user_email
from apps.batches.models import Batch
from apps.interns.models import InternProfile, InternRegistrationRequest


class InternListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    status = serializers.CharField(source="user.status", read_only=True)

    class Meta:
        model = InternProfile
        fields = (
            "id",
            "name",
            "email",
            "status",
            "batch",
            "intern_role",
            "rendered_hours",
            "required_hours",
            "assessment_score",
        )


class InternDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    status = serializers.ChoiceField(choices=User.StatusChoices.choices, required=False)
    password = serializers.CharField(write_only=True, required=False, trim_whitespace=False)
    batch = serializers.PrimaryKeyRelatedField(
        queryset=Batch.objects.all(),
        required=False,
        allow_null=True,
    )
    company_account_password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    class Meta:
        model = InternProfile
        fields = (
            "id",
            "name",
            "email",
            "status",
            "password",
            "batch",
            "school",
            "intern_role",
            "phone",
            "github_username",
            "required_hours",
            "rendered_hours",
            "start_date",
            "birthdate",
            "avatar",
            "company_account_email",
            "company_account_password",
            "assessment_required",
            "assessment_completed_at",
            "assessment_score",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "assessment_completed_at",
            "assessment_score",
            "created_at",
            "updated_at",
        )

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_email(self, value):
        user = getattr(self.instance, "user", None)
        return validate_unique_user_email(value, instance=user)

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        birthdate = attrs.get("birthdate", getattr(self.instance, "birthdate", None))
        if start_date and birthdate and birthdate >= start_date:
            raise serializers.ValidationError(
                {"birthdate": ["Birthdate must be earlier than start date."]}
            )

        request = self.context.get("request")
        if request and request.method == "POST":
            required_fields = (
                "name",
                "email",
                "password",
                "school",
                "phone",
                "start_date",
                "birthdate",
            )
            missing = [field for field in required_fields if not attrs.get(field)]
            if missing:
                raise serializers.ValidationError(
                    {field: ["This field is required."] for field in missing}
                )
        return attrs


class InternRegistrationRequestSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    intern_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = InternRegistrationRequest
        fields = (
            "id",
            "name",
            "email",
            "password",
            "github_username",
            "school",
            "phone",
            "birthdate",
            "start_date",
            "required_hours",
            "status",
            "created_at",
            "decided_at",
            "intern_id",
        )
        read_only_fields = ("id", "status", "created_at", "decided_at", "intern_id")

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_email(self, value):
        return validate_unique_user_email(value)


class AssessmentResultSummarySerializer(serializers.Serializer):
    assessment_id = serializers.UUIDField()
    assessment_title = serializers.CharField()
    score = serializers.CharField()
    completed = serializers.BooleanField()
    completed_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()


class HoursBreakdownSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    email = serializers.EmailField()
    rendered_hours = serializers.CharField()
    required_hours = serializers.CharField()
