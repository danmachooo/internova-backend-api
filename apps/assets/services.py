from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.assets.models import Laptop, LaptopIssueReport


class LaptopService:
    @staticmethod
    def save_laptop(*, validated_data):
        status_value = validated_data.get("status", Laptop.StatusChoices.AVAILABLE)
        assigned_to = validated_data.get("assigned_to")
        if assigned_to and status_value == Laptop.StatusChoices.AVAILABLE:
            validated_data["status"] = Laptop.StatusChoices.ASSIGNED
        if not assigned_to and status_value == Laptop.StatusChoices.ASSIGNED:
            validated_data["status"] = Laptop.StatusChoices.AVAILABLE
        laptop = Laptop.objects.create(**validated_data)
        return laptop

    @staticmethod
    def update_laptop(*, laptop, validated_data):
        for field, value in validated_data.items():
            setattr(laptop, field, value)
        LaptopService._sync_assignment_status(laptop=laptop)
        update_fields = list(validated_data.keys())
        if "status" not in update_fields:
            update_fields.append("status")
        if "updated_at" not in update_fields:
            update_fields.append("updated_at")
        laptop.save(update_fields=update_fields)
        return laptop

    @staticmethod
    def _sync_assignment_status(*, laptop):
        if laptop.assigned_to_id and laptop.status == Laptop.StatusChoices.AVAILABLE:
            laptop.status = Laptop.StatusChoices.ASSIGNED
        if not laptop.assigned_to_id and laptop.status == Laptop.StatusChoices.ASSIGNED:
            laptop.status = Laptop.StatusChoices.AVAILABLE


class LaptopIssueReportService:
    @staticmethod
    def submit_report(*, intern, validated_data):
        laptop = validated_data["laptop"]
        if laptop.assigned_to != intern:
            raise ValidationError({"laptop": ["You can only report issues for your assigned laptop."]})

        return LaptopIssueReport.objects.create(
            intern=intern,
            laptop=laptop,
            description=validated_data["description"],
        )

    @staticmethod
    def update_report(*, report, validated_data, resolved_by):
        status_value = validated_data.get("status", report.status)
        admin_note = validated_data.get("admin_note", report.admin_note)

        report.status = status_value
        report.admin_note = admin_note
        if status_value == LaptopIssueReport.StatusChoices.RESOLVED:
            report.resolved_by = resolved_by
            report.resolved_at = timezone.now()
        else:
            report.resolved_by = None
            report.resolved_at = None

        report.save(
            update_fields=["status", "admin_note", "resolved_by", "resolved_at", "updated_at"]
        )
        return report
