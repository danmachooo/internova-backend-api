from django.db.models import Exists, OuterRef
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin, IsAdminOrIntern
from apps.notifications.models import Notification, NotificationReadState
from apps.notifications.serializers import NotificationSerializer
from apps.notifications.services import NotificationService


class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAdminOrIntern]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    http_method_names = ["get", "post", "delete"]
    ordering_fields = ("created_at", "type")

    def get_permissions(self):
        if self.action in ("create", "destroy"):
            return [IsAdmin()]
        return [IsAdminOrIntern()]

    def get_queryset(self):
        user = self.request.user
        audiences = ["all"]
        if user.role == User.RoleChoices.INTERN:
            audiences.extend(["intern", f"intern:{user.id}"])
        else:
            audiences.append("admin")

        read_state_queryset = NotificationReadState.objects.filter(
            notification=OuterRef("pk"),
            reader=user,
        )
        return (
            self.queryset.filter(audience__in=audiences)
            .annotate(read=Exists(read_state_queryset))
            .order_by("-created_at")
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification = NotificationService.push(**serializer.validated_data)
        return Response(
            self.get_serializer(notification).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="read")
    def read(self, request, pk=None):
        notification = self.get_object()
        NotificationService.mark_read(notification=notification, reader=request.user)
        refreshed = self.get_queryset().get(pk=notification.pk)
        return Response(self.get_serializer(refreshed).data, status=status.HTTP_200_OK)
