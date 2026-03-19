from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    read = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ("id", "title", "message", "type", "audience", "read", "created_at")
        read_only_fields = ("id", "read", "created_at")

    def get_read(self, obj):
        return bool(getattr(obj, "read", False))
