from django.test import TestCase

from apps.calendar.models import CalendarSettings


class CalendarSettingsModelTests(TestCase):
    def test_calendar_settings_get_returns_singleton(self):
        first = CalendarSettings.get()
        second = CalendarSettings.get()

        self.assertEqual(first.pk, 1)
        self.assertEqual(second.pk, 1)
        self.assertEqual(CalendarSettings.objects.count(), 1)

    def test_calendar_settings_save_enforces_singleton_id(self):
        settings = CalendarSettings(id=9, weekend_days=[0, 6])
        settings.save()

        self.assertEqual(settings.pk, 1)
