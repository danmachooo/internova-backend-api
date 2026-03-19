from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.batches.models import Batch


class BatchModelTests(TestCase):
    def test_batch_defaults_to_active_status_and_zero_progress(self):
        batch = Batch.objects.create(
            name="Batch 2026-A",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 6, 1),
        )

        self.assertEqual(batch.status, Batch.StatusChoices.ACTIVE)
        self.assertEqual(batch.progress, 0)

    def test_batch_clean_rejects_end_date_before_start_date(self):
        batch = Batch(
            name="Batch 2026-B",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 3, 1),
        )

        with self.assertRaises(ValidationError):
            batch.clean()
