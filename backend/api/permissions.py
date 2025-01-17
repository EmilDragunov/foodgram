"""Пермишены."""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """Проверяет, является ли пользователь автором объекта."""

    def has_object_permission(self, request, view, obj):
        """Получение объекта."""
        return request.method in SAFE_METHODS or obj.author == request.user
