"""Фильтры для рецептов."""
from django_filters import rest_framework as filters
from recipes.models import (
    ShoppingCart, Favorite, Recipe, Tag, Ingredient)


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    author = filters.NumberFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ('tags', 'is_favorited', 'author')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            user = self.request.user
            return queryset.filter(favorites__user=user)
        return queryset
    

class IngredientFilter(filters.FilterSet):
    """Фильтр для ингридиентов"""
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']
