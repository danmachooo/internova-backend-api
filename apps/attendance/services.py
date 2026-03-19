from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.attendance.models import AttendanceRecord
from apps.accounts.models import User


class AttendanceService:
    LATE_THRESHOLD = time(9, 0)
    END_OF_DAY = time(17, 0)
    OVERTIME_THRESHOLD = time(18, 0)

    @staticmethod
    def compute_hours(*, login_time, logout_time):
        if not login_time or not logout_time:
            return Decimal("0.00")

        login_dt = datetime.combine(timezone.localdate(), login_time)
        logout_dt = datetime.combine(timezone.localdate(), logout_time)
        total_seconds = max((logout_dt - login_dt).total_seconds(), 0)
        hours = Decimal(total_seconds / 3600).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return hours

    @staticmethod
    def classify(*, login_time, logout_time):
        if not login_time:
            return AttendanceRecord.StatusChoices.ABSENT
        if logout_time and logout_time >= AttendanceService.OVERTIME_THRESHOLD:
            return AttendanceRecord.StatusChoices.OVERTIME
        if logout_time and logout_time < AttendanceService.END_OF_DAY:
            return AttendanceRecord.StatusChoices.UNDERTIME
        if login_time >= AttendanceService.LATE_THRESHOLD:
            return AttendanceRecord.StatusChoices.LATE
        return AttendanceRecord.StatusChoices.PRESENT

    @staticmethod
    @transaction.atomic
    def clock_in(*, intern):
        today = timezone.localdate()
        if AttendanceRecord.objects.filter(intern=intern, date=today).exists():
            raise ValidationError("You have already clocked in today.")

        current_time = timezone.localtime().time().replace(microsecond=0)
        record = AttendanceRecord.objects.create(
            intern=intern,
            date=today,
            login_time=current_time,
            hours=Decimal("0.00"),
            status=AttendanceService.classify(login_time=current_time, logout_time=None),
        )
        AttendanceService._sync_rendered_hours(intern=intern)
        return record

    @staticmethod
    @transaction.atomic
    def clock_out(*, intern):
        today = timezone.localdate()
        record = get_object_or_404(
            AttendanceRecord.objects.select_related("intern"),
            intern=intern,
            date=today,
        )
        if record.logout_time:
            raise ValidationError("You have already clocked out today.")
        if not record.login_time:
            raise ValidationError("You must clock in before clocking out.")

        current_time = timezone.localtime().time().replace(microsecond=0)
        record.logout_time = current_time
        record.hours = AttendanceService.compute_hours(
            login_time=record.login_time,
            logout_time=record.logout_time,
        )
        record.status = AttendanceService.classify(
            login_time=record.login_time,
            logout_time=record.logout_time,
        )
        record.save(update_fields=["logout_time", "hours", "status", "updated_at"])
        AttendanceService._sync_rendered_hours(intern=intern)
        return record

    @staticmethod
    def prepare_record_data(*, validated_data):
        login_time = validated_data.get("login_time")
        logout_time = validated_data.get("logout_time")
        validated_data["hours"] = AttendanceService.compute_hours(
            login_time=login_time,
            logout_time=logout_time,
        )
        validated_data["status"] = AttendanceService.classify(
            login_time=login_time,
            logout_time=logout_time,
        )
        return validated_data

    @staticmethod
    @transaction.atomic
    def save_record(*, validated_data):
        prepared_data = AttendanceService.prepare_record_data(validated_data=validated_data)
        record = AttendanceRecord.objects.create(**prepared_data)
        AttendanceService._sync_rendered_hours(intern=record.intern)
        return record

    @staticmethod
    @transaction.atomic
    def update_record(*, record, validated_data):
        prepared_data = AttendanceService.prepare_record_data(
            validated_data={
                "login_time": validated_data.get("login_time", record.login_time),
                "logout_time": validated_data.get("logout_time", record.logout_time),
            }
        )
        update_fields = []
        for field in ("login_time", "logout_time"):
            if field in validated_data:
                setattr(record, field, validated_data[field])
                update_fields.append(field)
        record.hours = prepared_data["hours"]
        record.status = prepared_data["status"]
        record.save(update_fields=[*set(update_fields + ["hours", "status", "updated_at"])])
        AttendanceService._sync_rendered_hours(intern=record.intern)
        return record

    @staticmethod
    def weekly_summary(*, week_start):
        normalized_start = week_start - timedelta(days=week_start.weekday())
        days = [normalized_start + timedelta(days=offset) for offset in range(5)]

        summary = []
        for current_date in days:
            day_records = AttendanceRecord.objects.filter(date=current_date)
            counts = {status: 0 for status, _ in AttendanceRecord.StatusChoices.choices}
            for record in day_records.only("status"):
                counts[record.status] += 1
            summary.append(
                {
                    "date": current_date.isoformat(),
                    **counts,
                }
            )
        return summary

    @staticmethod
    def _sync_rendered_hours(*, intern):
        from apps.interns.models import InternProfile

        total = (
            AttendanceRecord.objects.filter(intern=intern).aggregate(total=Sum("hours"))["total"]
            or Decimal("0.00")
        )
        profile = get_object_or_404(InternProfile, user=intern)
        profile.rendered_hours = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        profile.save(update_fields=["rendered_hours", "updated_at"])
        return profile
