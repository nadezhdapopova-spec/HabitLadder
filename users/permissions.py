from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Проверяет, является ли пользователь авторизованным и владельцем"""

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.owner == request.user


class IsProfileOwner(BasePermission):
    """Проверяет, является ли пользователь владельцем профиля"""

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.id == request.user.id
