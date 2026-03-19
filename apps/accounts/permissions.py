from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and request.user.role == User.RoleChoices.SUPERADMIN
        )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.role in User.admin_roles()
        )


class IsIntern(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.role == User.RoleChoices.INTERN
        )


class IsAdminOrIntern(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated)


class IsAdminOrSelf(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.role in User.admin_roles():
            return True

        if hasattr(obj, "user"):
            return obj.user == request.user

        if hasattr(obj, "intern"):
            return obj.intern == request.user

        return obj == request.user
