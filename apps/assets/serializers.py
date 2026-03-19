from rest_framework import serializers

from apps.accounts.models import User
from apps.assets.models import Laptop, LaptopIssueReport


class LaptopListSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Laptop
        fields = ("id", "brand", "serial_no", "assigned_to", "status")
        read_only_fields = ("id",)


class LaptopDetailSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.RoleChoices.INTERN),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Laptop
        fields = (
            "id",
            "brand",
            "serial_no",
            "ip_address",
            "assigned_to",
            "status",
            "accounts",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class LaptopIssueReportListSerializer(serializers.ModelSerializer):
    intern = serializers.PrimaryKeyRelatedField(read_only=True)
    laptop = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = LaptopIssueReport
        fields = ("id", "intern", "laptop", "status", "created_at")
        read_only_fields = fields


class LaptopIssueReportDetailSerializer(serializers.ModelSerializer):
    intern = serializers.PrimaryKeyRelatedField(read_only=True)
    resolved_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = LaptopIssueReport
        fields = (
            "id",
            "intern",
            "laptop",
            "description",
            "status",
            "admin_note",
            "resolved_by",
            "resolved_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "intern", "resolved_by", "resolved_at", "created_at", "updated_at")


class LaptopIssueReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaptopIssueReport
        fields = ("id", "laptop", "description", "status", "admin_note")
        read_only_fields = ("id", "status", "admin_note")


class LaptopIssueReportUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaptopIssueReport
        fields = ("status", "admin_note")

