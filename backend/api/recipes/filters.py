"""Фильтры для рецептов."""
import django_filters
from recipes.models import (
    ShoppingCart, Favorite, Recipe, Tag, Ingredient)


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов."""

    is_favorited = django_filters.ChoiceFilter(
        method='filter',
        choices=[('1', 'Да'), ('0', 'Нет')],
        label='В избранном'
    )
    is_in_shopping_cart = django_filters.ChoiceFilter(
        method='filter',
        choices=[('1', 'Да'), ('0', 'Нет')],
        label='В списке покупок'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        label='Теги'
    )

    class Meta:
        """Мета данные."""

        model = Recipe
        fields = ['author']

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр для избранного."""
        if not self.request.user.is_authenticated:
            return queryset
        if value == '1':
            value = True
        elif value == '0':
            value = False
        else:
            return queryset
        result = Favorite.objects.filter(
            user=self.request.user).values('recipe')
        if value:
            return queryset.filter(id__in=result)
        return queryset.exclude(id__in=result)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр для списка покупок."""
        if not self.request.user.is_authenticated:
            return queryset
        if value == '1':
            value = True
        elif value == '0':
            value = False
        else:
            return queryset
        result = ShoppingCart.objects.filter(
            user=self.request.user).values('recipe')
        if value:
            return queryset.filter(id__in=result)
        return queryset.exclude(id__in=result)


class IngredientFilter(django_filters.FilterSet):
    """Фильтр для ингридиентов."""

    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        """Мета данные."""

        model = Ingredient
        fields = ['name']
