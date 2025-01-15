"""Админ-зона рецептов."""
from django.contrib import admin
from recipes.models import (
    ShoppingCart, Favorite, Ingredient, Recipe, RecipeIngredient, Tag
)
from django.utils.html import format_html


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Ингредиент."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Тег."""

    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}


class RecipeIngredientInline(admin.TabularInline):
    """Количество ингредиентов."""

    model = RecipeIngredient
    extra = 1
    min_num = 2


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Количество ингредиентов."""

    list_display = ('recipe', 'ingredient', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Рецепт."""

    list_display = ('name', 'author', 'favorites_count', 'image_preview')
    search_fields = ('author__username', 'name', 'tags__name')
    filter_horizontal = ('tags',)
    list_filter = ('tags', 'author')
    inlines = (RecipeIngredientInline,)

    @admin.display(description='В избранном')
    def favorites_count(self, obj):
        """В избранном."""
        return obj.favorites.count()

    @admin.display(description='Картинка рецепта')
    def image_preview(self, obj):
        """Отображает картинку рецепта."""
        if obj.image:
            return format_html(
                '<img src="{}" alt="Image" '
                'style="max-height: 100px; max-width: 100px;"/>',
                obj.image.url
            )
        return 'Нет изображения'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Избранные рецепты."""

    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Список покупок."""

    list_display = ('user', 'recipe')
