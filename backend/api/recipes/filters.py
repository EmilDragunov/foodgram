"""Фильтры для рецептов."""
from django_filters import rest_framework as filters
from recipes.models import (
    ShoppingCart, Favorite, Recipe, Tag, Ingredient)


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов"""
    is_favorited = filters.ChoiceFilter(
        method='filter',
        choices=[('1', 'Yes'), ('0', 'No')],
        label='Is Favorited'
    )
    is_in_shopping_cart = filters.ChoiceFilter(
        method='filter',
        choices=[('1', 'Yes'), ('0', 'No')],
        label='Is in Shopping Cart'
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        label='Теги'
    )

    class Meta:
        model = Recipe
        fields = ['author']

    def filter(self, queryset, name, value):
        """Фильтр избраное и список покупок"""
        if value == '1':
            value = True
        elif value == '0':
            value = False
        else:
            return queryset

        if name == 'is_favorited':
            model = Favorite
        elif name == 'is_in_shopping_cart':
            model = ShoppingCart

        if not self.request.user.is_authenticated:
            return queryset

        result = model.objects.filter(
            user=self.request.user).values('recipe')
        if value:
            return queryset.filter(id__in=result)
        else:
            return queryset.exclude(id__in=result)


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингридиентов"""
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']
