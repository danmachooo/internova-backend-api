from datetime import date, timedelta

from django.utils.dateparse import parse_date
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin, IsAdminOrSelf, IsIntern
from apps.attendance.filters import AttendanceFilter
from apps.attendance.models import AttendanceRecord
from apps.attendance.serializers import AttendanceRecordSerializer
from apps.attendance.services import AttendanceService


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceRecordSerializer
    filterset_class = AttendanceFilter
    ordering_fields = ("date", "created_at", "hours")
    http_method_names = ["get", "post", "patch"]

    def get_queryset(self):
        queryset = AttendanceRecord.objects.select_related("intern").all()
        if self.request.user.role == self.request.user.RoleChoices.INTERN:
            return queryset.filter(intern=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action == "my":
            return [IsIntern()]
        if self.action in {"create", "partial_update", "list"}:
            return [IsAdmin()]
        return [IsAdminOrSelf()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = AttendanceService.save_record(validated_data=serializer.validated_data)
        return Response(self.get_serializer(record).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        record = self.get_object()
        serializer = self.get_serializer(record, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_record = AttendanceService.update_record(
            record=record,
            validated_data=serializer.validated_data,
        )
        return Response(self.get_serializer(updated_record).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="my")
    def my(self, request):
        queryset = self.get_queryset().filter(intern=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClockInView(APIView):
    permission_classes = [IsIntern]

    def post(self, request):
        record = AttendanceService.clock_in(intern=request.user)
        return Response(
            {
                "message": "Clocked in successfully.",
                "record": AttendanceRecordSerializer(record).data,
            },
            status=status.HTTP_201_CREATED,
        )


class ClockOutView(APIView):
    permission_classes = [IsIntern]

    def post(self, request):
        record = AttendanceService.clock_out(intern=request.user)
        return Response(
            {
                "message": "Clocked out successfully.",
                "record": AttendanceRecordSerializer(record).data,
            },
            status=status.HTTP_200_OK,
        )


class WeeklyAttendanceSummaryView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        week_start_param = request.query_params.get("week_start")
        parsed = parse_date(week_start_param) if week_start_param else None
        if week_start_param and parsed is None:
            raise ValidationError({"week_start": ["Use YYYY-MM-DD format."]})
        week_start = parsed or timezone.localdate()
        summary = AttendanceService.weekly_summary(week_start=week_start)
        return Response(summary, status=status.HTTP_200_OK)
