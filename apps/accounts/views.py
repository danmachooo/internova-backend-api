from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.filters import AdminUserFilter
from apps.accounts.models import User
from apps.accounts.permissions import IsSuperAdmin
from apps.accounts.serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    MeSerializer,
    UserDetailSerializer,
    UserListSerializer,
)
from apps.accounts.services import AdminUserService, AuthService


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = AuthService.login(**serializer.validated_data)
        return Response(
            {
                "access": payload["access"],
                "refresh": payload["refresh"],
                "user": UserDetailSerializer(
                    payload["user"], context={"request": request}
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.logout(refresh_token=serializer.validated_data["refresh"])
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(MeSerializer(request.user).data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = MeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = AuthService.update_profile(
            user=request.user,
            validated_data=serializer.validated_data,
        )
        return Response(MeSerializer(user).data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        AuthService.change_password(
            user=request.user,
            old_password=serializer.validated_data["old_password"],
            new_password=serializer.validated_data["new_password"],
        )
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)


class AdminUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperAdmin]
    filterset_class = AdminUserFilter
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        return User.objects.filter(role__in=User.admin_roles()).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        return UserDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = AdminUserService.create_admin(validated_data=serializer.validated_data)
        return Response(
            UserDetailSerializer(user, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_user = AdminUserService.update_admin(
            user=user,
            validated_data=serializer.validated_data,
        )
        return Response(
            UserDetailSerializer(updated_user, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )
