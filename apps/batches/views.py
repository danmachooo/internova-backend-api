from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin
from apps.batches.filters import BatchFilter
from apps.batches.models import Batch
from apps.batches.serializers import (
    BatchDetailSerializer,
    BatchInternSerializer,
    BatchListSerializer,
)
from apps.batches.services import BatchService


class BatchViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    filterset_class = BatchFilter
    search_fields = ("name",)
    ordering_fields = ("start_date", "end_date", "progress", "created_at")

    def get_queryset(self):
        return Batch.objects.all().order_by("-start_date", "-created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return BatchListSerializer
        return BatchDetailSerializer

    @action(detail=True, methods=["get"], url_path="interns")
    def interns(self, request, pk=None):
        batch = self.get_object()
        payload = BatchService.list_batch_interns(batch=batch)
        serializer = BatchInternSerializer(payload, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
