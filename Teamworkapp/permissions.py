# teamworkapp/permissions.py
from rest_framework import permissions

class IsITOfficer(permissions.BasePermission):
    """
    Allow access only to users with role 'it_officer' or superuser.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return getattr(user, "role", None) == "it_officer" or user.is_superuser


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admins can perform non-read-only actions. Others read-only.
    """
    def has_permission(self, request, view):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        return user and user.is_authenticated and (user.is_superuser or getattr(user, "role", None) == "admin")
