from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.attendance.views import (
    AttendanceViewSet,
    ClockInView,
    ClockOutView,
    WeeklyAttendanceSummaryView,
)


router = DefaultRouter()
router.register("attendance", AttendanceViewSet, basename="attendance")

urlpatterns = [
    path("attendance/clock-in/", ClockInView.as_view(), name="attendance-clock-in"),
    path("attendance/clock-out/", ClockOutView.as_view(), name="attendance-clock-out"),
    path(
        "attendance/summary/weekly/",
        WeeklyAttendanceSummaryView.as_view(),
        name="attendance-summary-weekly",
    ),
]

urlpatterns += router.urls
