from rest_framework import serializers

from apps.calendar.models import CalendarEvent, CalendarSettings, Holiday


class CalendarEventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = ("id", "title", "date", "time", "type")
        read_only_fields = ("id",)


class CalendarEventDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = (
            "id",
            "title",
            "date",
            "time",
            "type",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class HolidayListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = ("id", "date", "name")
        read_only_fields = ("id",)


class HolidayDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = ("id", "date", "name", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class CalendarSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarSettings
        fields = ("id", "weekend_days", "updated_at")
        read_only_fields = ("id", "updated_at")

    def validate_weekend_days(self, value):
        if not value:
            raise serializers.ValidationError("weekend_days cannot be empty.")
        if any(day not in range(7) for day in value):
            raise serializers.ValidationError("weekend_days values must be between 0 and 6.")
        return sorted(set(value))
