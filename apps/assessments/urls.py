from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.assessments.views import (
    AssessmentPageDetailView,
    AssessmentQuestionCreateView,
    AssessmentQuestionDetailView,
    AssessmentViewSet,
    InternAttemptViewSet,
)


router = DefaultRouter()
router.register("assessments", AssessmentViewSet, basename="assessment")
router.register("attempts", InternAttemptViewSet, basename="attempt")

urlpatterns = [
    path(
        "assessments/<uuid:assessment_id>/pages/<uuid:page_id>/",
        AssessmentPageDetailView.as_view(),
        name="assessment-page-detail",
    ),
    path(
        "assessments/<uuid:assessment_id>/pages/<uuid:page_id>/questions/",
        AssessmentQuestionCreateView.as_view(),
        name="assessment-question-create",
    ),
    path(
        "assessments/<uuid:assessment_id>/pages/<uuid:page_id>/questions/<uuid:q_id>/",
        AssessmentQuestionDetailView.as_view(),
        name="assessment-question-detail",
    ),
]

urlpatterns += router.urls
