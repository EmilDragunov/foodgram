"""Приложение АPI."""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """АPI."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
