"""Вьюсеты для рецептов."""
from rest_framework import viewsets
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from recipes.models import Ingredient, Tag, Recipe, Favorite, ShoppingCart
from .serializers import (IngredientSerializer, TagSerializer,
                          RecipeSerializer, RecipePostSerializer)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .filters import RecipeFilter, IngredientFilter
from django_filters.rest_framework import DjangoFilterBackend
from api.pagination import RecipePagination
from api.permissions import IsOwner
from django.shortcuts import get_object_or_404, redirect
from rest_framework.decorators import api_view, permission_classes


User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингредиенты."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ModelViewSet):
    """Теги."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""

    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwner)
    filterset_class = RecipeFilter

    def get_queryset(self):
        return Recipe.objects.all().select_related(
            'author').prefetch_related('tags', 'ingredients')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipePostSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['GET'], detail=True, permission_classes=(AllowAny,))
    def get_recipe(self, request, pk=None):
        recipe = self.get_object()
        serializer = RecipeSerializer(recipe, context={'request': request})
        return Response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        """Добавление и удаление из избранного."""
        user = request.user
        recipe = self.get_object()
        if request.method == 'POST':
            if user.favorites.filter(recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            user.favorites.create(recipe=recipe)
            return Response({'message': 'Рецепт добавлен в избранное'},
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if user.favorites.filter(recipe=recipe).exists():
                user.favorites.filter(recipe=recipe).delete()
                return Response({'message': 'Рецепт удалён из избранного'},
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт не был добавлен в избранное'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['GET'], detail=True,
            permission_classes=[AllowAny])
    def get_link(self, request, pk=None):
        """Получение короткой ссылки."""
        result = get_object_or_404(Recipe, pk=pk)
        return Response(
            {"short-link": request.build_absolute_uri(f"/s/{result.link}/")},
            status=status.HTTP_200_OK
        )

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        """Добавление и удаление в список покупок."""
        user = request.user
        recipe = self.get_object()
        if request.method == 'POST':
            if user.shopping_cart.filter(recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже в списке покупок'},
                                status=status.HTTP_400_BAD_REQUEST)
            user.shopping_cart.create(recipe=recipe)
            return Response({'message': 'Рецепт добавлен в список покупок'},
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if user.shopping_cart.filter(recipe=recipe).exists():
                user.shopping_cart.filter(recipe=recipe).delete()
                return Response({'message': 'Рецепт удалён из списка покупок'},
                                status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепт не был добавлен в список покупок'},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['GET'], detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Получение файла списка покупок."""
        user = request.user
        ingredients = {}
        recipes = user.shopping_cart.all()
        for recipe in recipes:
            for item in recipe.recipe.recipeingredient_set.all():
                if item.ingredient.name in ingredients:
                    ingredients[item.ingredient.name]['amount'] += item.amount
                else:
                    ingredients[item.ingredient.name] = {
                        'amount': item.amount,
                        'unit': item.ingredient.measurement_unit}

        result = ''
        for key, value in ingredients.items():
            result += f'{key} {value["amount"]} {value["unit"]}\n'
        response = Response(result, content_type='text/plain',
                            status=status.HTTP_200_OK)
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response


@api_view(['GET'])
@permission_classes([AllowAny])
def short_link(request, link):
    """Короткая ссылка."""
    recipe = get_object_or_404(Recipe, link=link)
    return redirect(f'/recipes/{recipe.id}/')
