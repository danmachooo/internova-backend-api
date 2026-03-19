from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.dar.models import DailyActivityReport


class DailyActivityReportService:
    @staticmethod
    def submit_report(*, intern, validated_data):
        report_date = validated_data["date"]

        if DailyActivityReport.objects.filter(intern=intern, date=report_date).exists():
            raise ValidationError("You have already submitted a DAR for this date.")

        current_time = timezone.localtime().time().replace(microsecond=0)
        return DailyActivityReport.objects.create(
            intern=intern,
            date=report_date,
            file=validated_data["file"],
            upload_time=current_time,
            status=DailyActivityReport.StatusChoices.SUBMITTED,
        )

    @staticmethod
    def missing_reports(*, report_date):
        submitted_ids = DailyActivityReport.objects.filter(
            date=report_date,
            status=DailyActivityReport.StatusChoices.SUBMITTED,
        ).values_list("intern_id", flat=True)

        return User.objects.filter(
            role=User.RoleChoices.INTERN,
            status=User.StatusChoices.ACTIVE,
        ).exclude(id__in=submitted_ids)
