from django.test import TestCase

from apps.feature_access.models import FeatureAccessConfig


class FeatureAccessConfigModelTests(TestCase):
    def test_feature_access_get_returns_singleton(self):
        first = FeatureAccessConfig.get()
        second = FeatureAccessConfig.get()

        self.assertEqual(first.pk, 1)
        self.assertEqual(second.pk, 1)
        self.assertEqual(FeatureAccessConfig.objects.count(), 1)

    def test_feature_access_save_enforces_singleton_and_always_on_features(self):
        config = FeatureAccessConfig(
            id=9,
            admin_features={"dashboard": False, "leaves": False},
            intern_features={"dashboard": False, "notifications": False, "profile": False},
        )

        config.save()

        self.assertEqual(config.pk, 1)
        self.assertTrue(config.admin_features["dashboard"])
        self.assertTrue(config.admin_features["leaves"])
        self.assertTrue(config.admin_features["profile"])
        self.assertTrue(config.admin_features["notifications"])
        self.assertTrue(config.intern_features["dashboard"])
        self.assertTrue(config.intern_features["notifications"])
        self.assertTrue(config.intern_features["profile"])

