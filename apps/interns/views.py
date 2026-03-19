from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin, IsAdminOrSelf
from apps.interns.filters import InternFilter
from apps.interns.models import InternProfile, InternRegistrationRequest
from apps.interns.serializers import (
    AssessmentResultSummarySerializer,
    HoursBreakdownSerializer,
    InternDetailSerializer,
    InternListSerializer,
    InternRegistrationRequestSerializer,
)
from apps.interns.services import InternService


class InternRoleListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        payload = [
            {"value": value, "label": label}
            for value, label in InternProfile.InternRoleChoices.choices
        ]
        return Response(payload, status=status.HTTP_200_OK)


class InternViewSet(viewsets.ModelViewSet):
    filterset_class = InternFilter
    search_fields = ("user__name", "user__email", "school", "github_username")
    ordering_fields = ("created_at", "required_hours", "rendered_hours", "user__name")
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        queryset = InternProfile.objects.select_related("user", "batch")
        if self.request.user.role == self.request.user.RoleChoices.INTERN:
            return queryset.filter(user=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action in {"list", "create", "destroy", "hours_breakdown", "attempts"}:
            return [IsAdmin()]
        return [IsAdminOrSelf()]

    def get_serializer_class(self):
        if self.action == "list":
            return InternListSerializer
        return InternDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        profile = InternService.create_intern(validated_data=serializer.validated_data)
        response_serializer = InternDetailSerializer(profile, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(
            profile,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated_profile = InternService.update_intern(
            profile=profile,
            validated_data=serializer.validated_data,
            actor=request.user,
        )
        return Response(
            InternDetailSerializer(updated_profile, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        profile = self.get_object()
        InternService.delete_intern(profile=profile)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="hours-breakdown")
    def hours_breakdown(self, request):
        payload = InternService.hours_breakdown(batch_id=request.query_params.get("batch_id"))
        serializer = HoursBreakdownSerializer(payload, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="attempts")
    def attempts(self, request, pk=None):
        profile = self.get_object()
        payload = InternService.list_attempt_summaries(intern=profile.user)
        serializer = AssessmentResultSummarySerializer(payload, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegistrationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = InternRegistrationRequestSerializer
    http_method_names = ["get", "post"]

    def get_queryset(self):
        return InternRegistrationRequest.objects.select_related("intern").all()

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAdmin()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registration = InternService.submit_registration(validated_data=serializer.validated_data)
        response_serializer = self.get_serializer(registration)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        registration = InternService.approve_registration(pk, request.user)
        serializer = self.get_serializer(registration)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def deny(self, request, pk=None):
        registration = InternService.deny_registration(pk, request.user)
        serializer = self.get_serializer(registration)
        return Response(serializer.data, status=status.HTTP_200_OK)
