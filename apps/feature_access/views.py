from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsSuperAdmin
from apps.feature_access.models import FeatureAccessConfig
from apps.feature_access.serializers import FeatureAccessConfigSerializer


class FeatureAccessView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        serializer = FeatureAccessConfigSerializer(FeatureAccessConfig.get())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        config = FeatureAccessConfig.get()
        serializer = FeatureAccessConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

