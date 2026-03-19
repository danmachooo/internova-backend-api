from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin
from apps.calendar.models import CalendarEvent, CalendarSettings, Holiday
from apps.calendar.serializers import (
    CalendarEventDetailSerializer,
    CalendarEventListSerializer,
    CalendarSettingsSerializer,
    HolidayDetailSerializer,
    HolidayListSerializer,
)


class CalendarEventViewSet(viewsets.ModelViewSet):
    queryset = CalendarEvent.objects.all()
    http_method_names = ["get", "post", "patch", "delete"]
    ordering_fields = ("date", "time", "created_at")

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            return [IsAuthenticated()]
        return [IsAdmin()]

    def get_serializer_class(self):
        if self.action == "list":
            return CalendarEventListSerializer
        return CalendarEventDetailSerializer


class HolidayViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Holiday.objects.all()
    serializer_class = HolidayDetailSerializer
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action == "create":
            return HolidayListSerializer
        return HolidayDetailSerializer


class CalendarSettingsView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAdmin()]
        return [IsAdmin()]

    def get(self, request):
        serializer = CalendarSettingsSerializer(CalendarSettings.get())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        settings = CalendarSettings.get()
        serializer = CalendarSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
