from rest_framework.permissions import BasePermission


class IsAdministratorUser(BasePermission):
    """
    只允超级管理员用户访问。
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff and request.user.is_superuser)
