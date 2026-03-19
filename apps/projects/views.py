from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin
from apps.projects.models import Project
from apps.projects.serializers import ProjectDetailSerializer, ProjectListSerializer
from apps.projects.services import ProjectService


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    queryset = Project.objects.prefetch_related("assigned_interns").all()
    ordering_fields = ("name", "status", "start_date", "end_date", "created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        return ProjectDetailSerializer

    @action(detail=True, methods=["post"], url_path="assign")
    def assign(self, request, pk=None):
        project = self.get_object()
        project = ProjectService.assign_intern(
            project=project,
            intern_id=request.data.get("intern"),
        )
        serializer = self.get_serializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["delete"],
        url_path=r"assign/(?P<intern_id>[^/.]+)",
    )
    def unassign(self, request, pk=None, intern_id=None):
        project = self.get_object()
        project = ProjectService.unassign_intern(
            project=project,
            intern_id=intern_id,
        )
        serializer = self.get_serializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)
