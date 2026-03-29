from rest_framework.permissions import BasePermission


class IsAdminStaff(BasePermission):
    """
    Allows access only to staff members with role = 'admin'.
    """
    message = "Only admin staff members can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )