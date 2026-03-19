from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin, IsAdminOrSelf, IsIntern
from apps.assets.models import Laptop, LaptopIssueReport
from apps.assets.serializers import (
    LaptopDetailSerializer,
    LaptopIssueReportCreateSerializer,
    LaptopIssueReportDetailSerializer,
    LaptopIssueReportListSerializer,
    LaptopIssueReportUpdateSerializer,
    LaptopListSerializer,
)
from apps.assets.services import LaptopIssueReportService, LaptopService


class LaptopViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    queryset = Laptop.objects.select_related("assigned_to").all()
    ordering_fields = ("brand", "serial_no", "status", "created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return LaptopListSerializer
        return LaptopDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        laptop = LaptopService.save_laptop(validated_data=serializer.validated_data)
        return Response(self.get_serializer(laptop).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        laptop = self.get_object()
        serializer = self.get_serializer(laptop, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        laptop = LaptopService.update_laptop(
            laptop=laptop,
            validated_data=serializer.validated_data,
        )
        return Response(self.get_serializer(laptop).data, status=status.HTTP_200_OK)


class LaptopIssueReportViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrSelf]
    queryset = LaptopIssueReport.objects.select_related("intern", "laptop", "resolved_by").all()
    http_method_names = ["get", "post", "patch"]
    ordering_fields = ("created_at", "status", "resolved_at")

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.role == self.request.user.RoleChoices.INTERN:
            return queryset.filter(intern=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action == "create":
            return [IsIntern()]
        if self.action == "partial_update":
            return [IsAdmin()]
        return [IsAdminOrSelf()]

    def get_serializer_class(self):
        if self.action == "list":
            return LaptopIssueReportListSerializer
        if self.action == "create":
            return LaptopIssueReportCreateSerializer
        if self.action == "partial_update":
            return LaptopIssueReportUpdateSerializer
        return LaptopIssueReportDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = LaptopIssueReportService.submit_report(
            intern=request.user,
            validated_data=serializer.validated_data,
        )
        return Response(
            LaptopIssueReportDetailSerializer(report).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        report = self.get_object()
        serializer = self.get_serializer(report, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        report = LaptopIssueReportService.update_report(
            report=report,
            validated_data=serializer.validated_data,
            resolved_by=request.user,
        )
        return Response(
            LaptopIssueReportDetailSerializer(report).data,
            status=status.HTTP_200_OK,
        )
