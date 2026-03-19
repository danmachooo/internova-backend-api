from datetime import date

from django.test import TestCase

from apps.batches.models import Batch
from apps.batches.services import BatchService


class BatchServiceTests(TestCase):
    def test_list_batch_interns_returns_empty_list_when_interns_app_missing(self):
        batch = Batch.objects.create(
            name="Batch 2026-A",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 6, 1),
        )

        payload = BatchService.list_batch_interns(batch=batch)

        self.assertEqual(payload, [])
