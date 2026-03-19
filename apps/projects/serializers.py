from rest_framework import serializers

from apps.accounts.models import User
from apps.projects.models import Project


class AssignedInternSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name", "email")
        read_only_fields = fields


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "name", "status", "start_date", "end_date")
        read_only_fields = ("id",)


class ProjectDetailSerializer(serializers.ModelSerializer):
    assigned_interns = AssignedInternSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "status",
            "start_date",
            "end_date",
            "assigned_interns",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "assigned_interns")

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                {"end_date": ["end_date cannot be earlier than start_date."]}
            )
        return attrs
