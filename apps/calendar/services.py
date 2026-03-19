from datetime import timedelta

from apps.calendar.models import CalendarSettings, Holiday


class CalendarService:
    JS_TO_PYTHON = {0: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}

    @staticmethod
    def is_weekend(target_date):
        settings = CalendarSettings.get()
        python_weekend_days = {
            CalendarService.JS_TO_PYTHON[day] for day in settings.weekend_days
        }
        return target_date.weekday() in python_weekend_days

    @staticmethod
    def is_holiday(target_date):
        return Holiday.objects.filter(date=target_date).exists()

    @staticmethod
    def count_business_days(*, start_date, end_date):
        if start_date > end_date:
            return 0

        current_date = start_date
        business_days = 0
        while current_date <= end_date:
            if not CalendarService.is_weekend(current_date) and not CalendarService.is_holiday(
                current_date
            ):
                business_days += 1
            current_date += timedelta(days=1)
        return business_days

    @staticmethod
    def estimate_end_date(*, start_date, business_days):
        if business_days <= 0:
            return start_date

        current_date = start_date
        counted_days = 0
        while counted_days < business_days:
            if not CalendarService.is_weekend(current_date) and not CalendarService.is_holiday(
                current_date
            ):
                counted_days += 1
                if counted_days == business_days:
                    return current_date
            current_date += timedelta(days=1)
        return current_date
