# Django Third-party modules
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaffOrReadOnly(BasePermission):
    """
    Allow read for everyone, write only for staff/superuser.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission to only allow owners or admins to edit/delete.
    Assumes the model instance has a `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return hasattr(obj, "user") and obj.user == request.user


class IsSelfOrAdmin(BasePermission):
    """
    Permission for user resources: allow if the object is the current user or staff.
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj == request.user
