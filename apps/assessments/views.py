from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin, IsAdminOrSelf, IsIntern
from apps.assessments.filters import AssessmentFilter, InternAttemptFilter
from apps.assessments.models import (
    Assessment,
    AssessmentPage,
    AssessmentQuestion,
    InternAttempt,
)
from apps.assessments.serializers import (
    AssessmentAdminSerializer,
    AssessmentPageSerializer,
    AssessmentPageWriteSerializer,
    AssessmentQuestionWriteSerializer,
    AssessmentSerializer,
    AssessmentSubmitSerializer,
    InternAttemptSerializer,
)
from apps.assessments.services import AssessmentService


class AssessmentViewSet(viewsets.ModelViewSet):
    filterset_class = AssessmentFilter
    search_fields = ("title", "description")
    ordering_fields = ("created_at", "updated_at", "published_at", "title")
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        queryset = Assessment.objects.prefetch_related("pages__questions").all()
        if self.request.user.role == User.RoleChoices.INTERN:
            return queryset.filter(is_published=True)
        return queryset

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [IsAuthenticated()]
        return [IsAdmin()]

    def get_serializer_class(self):
        if self.request.user.role == User.RoleChoices.INTERN:
            return AssessmentSerializer
        return AssessmentAdminSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        assessment = self.get_object()
        assessment.publish()
        serializer = self.get_serializer(assessment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        assessment = self.get_object()
        assessment.unpublish()
        serializer = self.get_serializer(assessment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get", "post"], url_path="pages")
    def pages(self, request, pk=None):
        assessment = self.get_object()
        if request.method.lower() == "get":
            serializer = AssessmentPageSerializer(
                assessment.pages.all().order_by("order", "created_at"),
                many=True,
                context={"request": request},
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = AssessmentPageWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        page = serializer.save(assessment=assessment)
        response_serializer = AssessmentPageSerializer(page, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class AssessmentPageDetailView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, assessment_id, page_id):
        page = get_object_or_404(
            AssessmentPage.objects.select_related("assessment"),
            pk=page_id,
            assessment_id=assessment_id,
        )
        serializer = AssessmentPageWriteSerializer(page, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        page = serializer.save()
        return Response(
            AssessmentPageSerializer(page, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, assessment_id, page_id):
        page = get_object_or_404(
            AssessmentPage.objects.select_related("assessment"),
            pk=page_id,
            assessment_id=assessment_id,
        )
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssessmentQuestionCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, assessment_id, page_id):
        page = get_object_or_404(
            AssessmentPage.objects.select_related("assessment"),
            pk=page_id,
            assessment_id=assessment_id,
        )
        serializer = AssessmentQuestionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save(page=page)
        return Response(
            AssessmentPageSerializer(page, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class AssessmentQuestionDetailView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, assessment_id, page_id, q_id):
        question = get_object_or_404(
            AssessmentQuestion.objects.select_related("page__assessment"),
            pk=q_id,
            page_id=page_id,
            page__assessment_id=assessment_id,
        )
        serializer = AssessmentQuestionWriteSerializer(
            question,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, assessment_id, page_id, q_id):
        question = get_object_or_404(
            AssessmentQuestion.objects.select_related("page__assessment"),
            pk=q_id,
            page_id=page_id,
            page__assessment_id=assessment_id,
        )
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InternAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = InternAttemptSerializer
    filterset_class = InternAttemptFilter
    ordering_fields = ("created_at", "completed_at", "score")
    http_method_names = ["get", "post"]

    def get_queryset(self):
        queryset = InternAttempt.objects.select_related("intern", "assessment").all()
        if self.request.user.role == User.RoleChoices.INTERN:
            return queryset.filter(intern=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action == "create":
            return [IsIntern()]
        if self.action in {"submit"}:
            return [IsIntern()]
        return [IsAdminOrSelf()]

    def create(self, request, *args, **kwargs):
        assessment = get_object_or_404(Assessment, pk=request.data.get("assessment"))
        if not assessment.is_published:
            raise ValidationError("Interns can only start published assessments.")
        if InternAttempt.objects.filter(intern=request.user, assessment=assessment).exists():
            raise ValidationError("You already started this assessment.")

        try:
            attempt = InternAttempt.objects.create(intern=request.user, assessment=assessment)
        except IntegrityError as exc:
            raise ValidationError("You already started this assessment.") from exc
        serializer = self.get_serializer(attempt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        attempt = get_object_or_404(
            InternAttempt.objects.select_related("intern", "assessment"),
            pk=pk,
            intern=request.user,
        )
        serializer = AssessmentSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_attempt = AssessmentService.submit(
            attempt=attempt,
            answers=serializer.validated_data["answers"],
        )
        return Response(self.get_serializer(updated_attempt).data, status=status.HTTP_200_OK)
