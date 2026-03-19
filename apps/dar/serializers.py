from rest_framework import serializers

from apps.dar.models import DailyActivityReport


class DailyActivityReportListSerializer(serializers.ModelSerializer):
    intern = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = DailyActivityReport
        fields = (
            "id",
            "intern",
            "date",
            "file",
            "upload_time",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class DailyActivityReportDetailSerializer(DailyActivityReportListSerializer):
    pass


class DailyActivityReportCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)

    class Meta:
        model = DailyActivityReport
        fields = ("id", "date", "file", "upload_time", "status", "created_at", "updated_at")
        read_only_fields = ("id", "upload_time", "status", "created_at", "updated_at")

    def validate_file(self, value):
        content_type = getattr(value, "content_type", None)
        if content_type != "application/pdf":
            raise serializers.ValidationError("Only PDF files are accepted.")

        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB.")

        return value


