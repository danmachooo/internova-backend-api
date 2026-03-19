from rest_framework import serializers

from apps.accounts.models import User
from apps.attendance.models import AttendanceRecord


class AttendanceRecordSerializer(serializers.ModelSerializer):
    intern = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.RoleChoices.INTERN),
    )

    class Meta:
        model = AttendanceRecord
        fields = (
            "id",
            "intern",
            "date",
            "login_time",
            "logout_time",
            "hours",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "hours", "status", "created_at", "updated_at")


class ClockActionSerializer(serializers.Serializer):
    message = serializers.CharField()
    record = AttendanceRecordSerializer()
