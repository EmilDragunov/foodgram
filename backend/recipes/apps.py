"""Приложение рецептов."""
from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Рецепты."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    verbose_name = 'Рецепты'
