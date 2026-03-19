from datetime import date

from django.test import TestCase

from apps.calendar.models import CalendarSettings, Holiday
from apps.calendar.services import CalendarService


class CalendarServiceTests(TestCase):
    def setUp(self):
        CalendarSettings.get()

    def test_count_business_days_skips_weekends_and_holidays(self):
        Holiday.objects.create(date=date(2026, 3, 25), name="Midweek Holiday")

        total = CalendarService.count_business_days(
            start_date=date(2026, 3, 23),
            end_date=date(2026, 3, 29),
        )

        self.assertEqual(total, 4)

    def test_is_holiday_returns_true_for_registered_holiday(self):
        holiday_date = date(2026, 12, 25)
        Holiday.objects.create(date=holiday_date, name="Christmas Day")

        self.assertTrue(CalendarService.is_holiday(holiday_date))
        self.assertFalse(CalendarService.is_holiday(date(2026, 12, 24)))

    def test_is_weekend_uses_js_to_python_normalization(self):
        settings = CalendarSettings.get()
        settings.weekend_days = [0, 6]
        settings.save()

        self.assertTrue(CalendarService.is_weekend(date(2026, 3, 22)))
        self.assertTrue(CalendarService.is_weekend(date(2026, 3, 21)))
        self.assertFalse(CalendarService.is_weekend(date(2026, 3, 23)))
