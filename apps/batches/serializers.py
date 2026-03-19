from rest_framework import serializers

from apps.batches.models import Batch


class BatchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = (
            "id",
            "name",
            "start_date",
            "end_date",
            "status",
            "progress",
        )

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": ["End date must be on or after start date."]}
            )
        return attrs


class BatchDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = (
            "id",
            "name",
            "start_date",
            "end_date",
            "status",
            "progress",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": ["End date must be on or after start date."]}
            )
        return attrs


class BatchInternSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    email = serializers.EmailField()
