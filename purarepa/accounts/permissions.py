"""Custom DRF permissions for the Purarepa project."""

from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allow access to users with role='ADMIN' or is_staff=True.

    DRF's built-in IsAdminUser only checks is_staff, which does not
    match the custom role-based system used in this project.
    """

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN'
