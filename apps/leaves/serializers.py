from rest_framework import serializers

from apps.accounts.models import User
from apps.leaves.models import LeaveRequest


class LeaveRequestListSerializer(serializers.ModelSerializer):
    intern = serializers.PrimaryKeyRelatedField(read_only=True)
    decided_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = LeaveRequest
        fields = (
            "id",
            "intern",
            "from_date",
            "to_date",
            "business_days",
            "type",
            "status",
            "created_at",
        )
        read_only_fields = fields


class LeaveRequestDetailSerializer(serializers.ModelSerializer):
    intern = serializers.PrimaryKeyRelatedField(read_only=True)
    decided_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = LeaveRequest
        fields = (
            "id",
            "intern",
            "from_date",
            "to_date",
            "business_days",
            "type",
            "reason",
            "status",
            "admin_note",
            "decided_at",
            "decided_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "intern",
            "business_days",
            "status",
            "decided_at",
            "decided_by",
            "created_at",
            "updated_at",
        )


class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ("id", "from_date", "to_date", "business_days", "type", "reason", "admin_note")
        read_only_fields = ("id", "business_days")

    def validate(self, attrs):
        if attrs["from_date"] > attrs["to_date"]:
            raise serializers.ValidationError(
                {"to_date": ["to_date cannot be earlier than from_date."]}
            )
        return attrs


class LeaveDecisionSerializer(serializers.Serializer):
    admin_note = serializers.CharField(max_length=500, required=False, allow_blank=True)
