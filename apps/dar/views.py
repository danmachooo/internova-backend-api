from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin, IsAdminOrSelf, IsIntern
from apps.dar.models import DailyActivityReport
from apps.dar.serializers import (
    DailyActivityReportCreateSerializer,
    DailyActivityReportDetailSerializer,
    DailyActivityReportListSerializer,
)
from apps.dar.services import DailyActivityReportService


class DARViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ["get", "post", "delete"]
    ordering_fields = ("date", "created_at", "upload_time")

    def get_queryset(self):
        queryset = DailyActivityReport.objects.select_related("intern").all()
        if self.request.user.role == self.request.user.RoleChoices.INTERN:
            return queryset.filter(intern=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action == "create":
            return [IsIntern()]
        if self.action in {"list", "destroy", "missing"}:
            return [IsAdmin()]
        if self.action == "my":
            return [IsIntern()]
        return [IsAdminOrSelf()]

    def get_serializer_class(self):
        if self.action == "create":
            return DailyActivityReportCreateSerializer
        if self.action == "retrieve":
            return DailyActivityReportDetailSerializer
        return DailyActivityReportListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = DailyActivityReportService.submit_report(
            intern=request.user,
            validated_data=serializer.validated_data,
        )
        response_serializer = DailyActivityReportDetailSerializer(
            report,
            context=self.get_serializer_context(),
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="missing")
    def missing(self, request):
        report_date = timezone.localdate()
        date_param = request.query_params.get("date")
        if date_param:
            parsed_date = parse_date(date_param)
            if parsed_date is None:
                raise ValidationError({"date": ["Use YYYY-MM-DD format."]})
            report_date = parsed_date

        interns = DailyActivityReportService.missing_reports(report_date=report_date)
        data = [
            {
                "intern_id": str(intern.id),
                "intern_name": intern.name,
                "intern_email": intern.email,
                "date": report_date.isoformat(),
            }
            for intern in interns
        ]
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="my")
    def my(self, request):
        queryset = self.get_queryset().filter(intern=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = DailyActivityReportListSerializer(
                page,
                many=True,
                context=self.get_serializer_context(),
            )
            return self.get_paginated_response(serializer.data)

        serializer = DailyActivityReportListSerializer(
            queryset,
            many=True,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
