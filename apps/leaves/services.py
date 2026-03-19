from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.calendar.services import CalendarService
from apps.leaves.models import LeaveRequest


class LeaveService:
    @staticmethod
    def submit(*, intern, validated_data):
        from_date = validated_data["from_date"]
        to_date = validated_data["to_date"]
        if from_date > to_date:
            raise ValidationError({"to_date": ["to_date cannot be earlier than from_date."]})

        business_days = CalendarService.count_business_days(
            start_date=from_date,
            end_date=to_date,
        )
        if business_days <= 0:
            raise ValidationError(
                {"from_date": ["The selected leave range has no business days."]}
            )

        return LeaveRequest.objects.create(
            intern=intern,
            from_date=from_date,
            to_date=to_date,
            business_days=business_days,
            type=validated_data["type"],
            reason=validated_data["reason"],
            admin_note=validated_data.get("admin_note"),
        )

    @staticmethod
    @transaction.atomic
    def approve(*, leave, decided_by, admin_note=None):
        if leave.status != LeaveRequest.StatusChoices.PENDING:
            raise ValidationError("Only pending leave requests can be approved.")

        leave.status = LeaveRequest.StatusChoices.APPROVED
        leave.decided_at = timezone.now()
        leave.decided_by = decided_by
        leave.admin_note = admin_note if admin_note is not None else leave.admin_note
        leave.save(
            update_fields=["status", "decided_at", "decided_by", "admin_note", "updated_at"]
        )
        LeaveService._push_notification(
            leave=leave,
            title="Leave Approved",
            message=(
                f"Your leave from {leave.from_date} to {leave.to_date} has been approved."
            ),
            notification_type="success",
        )
        return leave

    @staticmethod
    @transaction.atomic
    def deny(*, leave, decided_by, admin_note=None):
        if leave.status != LeaveRequest.StatusChoices.PENDING:
            raise ValidationError("Only pending leave requests can be denied.")

        leave.status = LeaveRequest.StatusChoices.DENIED
        leave.decided_at = timezone.now()
        leave.decided_by = decided_by
        leave.admin_note = admin_note if admin_note is not None else leave.admin_note
        leave.save(
            update_fields=["status", "decided_at", "decided_by", "admin_note", "updated_at"]
        )
        LeaveService._push_notification(
            leave=leave,
            title="Leave Denied",
            message=(
                f"Your leave from {leave.from_date} to {leave.to_date} has been denied."
            ),
            notification_type="error",
        )
        return leave

    @staticmethod
    def _push_notification(*, leave, title, message, notification_type):
        try:
            from apps.notifications.services import NotificationService
        except (ImportError, ModuleNotFoundError):
            return

        NotificationService.push(
            title=title,
            message=message,
            audience=f"intern:{leave.intern_id}",
            type=notification_type,
        )
