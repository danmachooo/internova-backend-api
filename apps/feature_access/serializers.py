from rest_framework import serializers

from apps.feature_access.models import FeatureAccessConfig


class FeatureAccessConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureAccessConfig
        fields = ("id", "admin_features", "intern_features", "updated_at")
        read_only_fields = ("id", "updated_at")

    def validate_admin_features(self, value):
        return self._validate_feature_map(
            value,
            expected_keys=set(FeatureAccessConfig.DEFAULT_ADMIN_FEATURES.keys()),
            field_name="admin_features",
        )

    def validate_intern_features(self, value):
        return self._validate_feature_map(
            value,
            expected_keys=set(FeatureAccessConfig.DEFAULT_INTERN_FEATURES.keys()),
            field_name="intern_features",
        )

    def _validate_feature_map(self, value, *, expected_keys, field_name):
        if not isinstance(value, dict):
            raise serializers.ValidationError(f"{field_name} must be an object.")

        received_keys = set(value.keys())
        missing_keys = sorted(expected_keys - received_keys)
        extra_keys = sorted(received_keys - expected_keys)
        if missing_keys or extra_keys:
            messages = []
            if missing_keys:
                messages.append(f"missing keys: {', '.join(missing_keys)}")
            if extra_keys:
                messages.append(f"unknown keys: {', '.join(extra_keys)}")
            raise serializers.ValidationError("; ".join(messages))

        for key, enabled in value.items():
            if not isinstance(enabled, bool):
                raise serializers.ValidationError(f"{key} must be a boolean value.")

        return value

