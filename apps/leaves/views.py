from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin, IsAdminOrSelf, IsIntern
from apps.leaves.filters import LeaveRequestFilter
from apps.leaves.models import LeaveRequest
from apps.leaves.serializers import (
    LeaveDecisionSerializer,
    LeaveRequestCreateSerializer,
    LeaveRequestDetailSerializer,
    LeaveRequestListSerializer,
)
from apps.leaves.services import LeaveService


class LeaveRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrSelf]
    filterset_class = LeaveRequestFilter
    ordering_fields = ("created_at", "from_date", "to_date", "business_days")
    http_method_names = ["get", "post"]

    def get_queryset(self):
        queryset = LeaveRequest.objects.select_related("intern", "decided_by").all()
        if self.request.user.role == self.request.user.RoleChoices.INTERN:
            return queryset.filter(intern=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action == "create":
            return [IsIntern()]
        if self.action in {"approve", "deny"}:
            return [IsAdmin()]
        return [IsAdminOrSelf()]

    def get_serializer_class(self):
        if self.action == "list":
            return LeaveRequestListSerializer
        if self.action == "create":
            return LeaveRequestCreateSerializer
        return LeaveRequestDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leave = LeaveService.submit(
            intern=request.user,
            validated_data=serializer.validated_data,
        )
        response_serializer = LeaveRequestDetailSerializer(
            leave,
            context=self.get_serializer_context(),
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        leave = self.get_object()
        serializer = LeaveDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_leave = LeaveService.approve(
            leave=leave,
            decided_by=request.user,
            admin_note=serializer.validated_data.get("admin_note"),
        )
        return Response(
            LeaveRequestDetailSerializer(
                updated_leave,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def deny(self, request, pk=None):
        leave = self.get_object()
        serializer = LeaveDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_leave = LeaveService.deny(
            leave=leave,
            decided_by=request.user,
            admin_note=serializer.validated_data.get("admin_note"),
        )
        return Response(
            LeaveRequestDetailSerializer(
                updated_leave,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_200_OK,
        )
