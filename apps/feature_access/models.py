from django.db import models


class FeatureAccessConfig(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    admin_features = models.JSONField(default=dict)
    intern_features = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    DEFAULT_ADMIN_FEATURES = {
        "dashboard": True,
        "batches": True,
        "interns": True,
        "dar": True,
        "assessments": True,
        "projects": True,
        "laptops": True,
        "calendar": True,
        "leaves": True,
        "notifications": True,
        "profile": True,
        "adminManagement": False,
        "featureAccess": False,
    }
    DEFAULT_INTERN_FEATURES = {
        "dashboard": True,
        "attendance": True,
        "leave": True,
        "dar": True,
        "laptopIssue": True,
        "notifications": True,
        "profile": True,
    }
    ALWAYS_ON_ADMIN = {"dashboard", "profile", "notifications", "leaves"}
    ALWAYS_ON_INTERN = {"dashboard", "profile", "notifications"}

    def save(self, *args, **kwargs):
        self.pk = 1
        self.admin_features = self._normalize_features(
            self.admin_features,
            defaults=self.DEFAULT_ADMIN_FEATURES,
            always_on=self.ALWAYS_ON_ADMIN,
        )
        self.intern_features = self._normalize_features(
            self.intern_features,
            defaults=self.DEFAULT_INTERN_FEATURES,
            always_on=self.ALWAYS_ON_INTERN,
        )
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "admin_features": dict(cls.DEFAULT_ADMIN_FEATURES),
                "intern_features": dict(cls.DEFAULT_INTERN_FEATURES),
            },
        )
        return obj

    @staticmethod
    def _normalize_features(features, *, defaults, always_on):
        normalized = dict(defaults)
        if isinstance(features, dict):
            normalized.update(features)
        for feature_name in always_on:
            normalized[feature_name] = True
        return normalized

    def __str__(self):
        return "Feature Access Configuration"

    class Meta:
        db_table = "feature_access_featureaccessconfig"
        ordering = ["id"]

