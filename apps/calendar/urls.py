from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.calendar.views import CalendarEventViewSet, CalendarSettingsView, HolidayViewSet


router = DefaultRouter()
router.register("events", CalendarEventViewSet, basename="event")
router.register("calendar/holidays", HolidayViewSet, basename="holiday")

urlpatterns = [
    path("calendar/settings/", CalendarSettingsView.as_view(), name="calendar-settings"),
]

urlpatterns += router.urls
