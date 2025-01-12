"""Пермишены."""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """Проверяет, является ли пользователь автором объекта."""

    def has_object_permission(self, request, view, obj):
        """Получение объекта."""
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
