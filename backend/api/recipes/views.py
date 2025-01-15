"""Вьюсеты для рецептов."""
from rest_framework import viewsets
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from recipes.models import Ingredient, Tag, Recipe, Favorite, ShoppingCart
from .serializers import (
    TagSerializer, RecipeSerializer, IngredientSerializer,
    AddRecipeSerializer, AddFavoriteAndShoppingCartSerializer)
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
from django.http import HttpResponse
from api.utils import add_method, remove_method

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для рецептов."""

    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwner]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        """Получает queryset рецептов."""
        return Recipe.objects.all().select_related(
            'author').prefetch_related('tags', 'ingredients')

    def get_serializer_class(self):
        """Определяет сериализатор на основе действия."""
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return AddRecipeSerializer

    def perform_create(self, serializer):
        """Сохраняет автора рецепта."""
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=['POST'], url_path='favorite',
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавляет рецепт в избранное."""
        return add_method(
            model=Recipe,
            request=request,
            pk=pk,
            serializer_class=AddFavoriteAndShoppingCartSerializer,
            related_field='recipe',
            model_serializer=Favorite
        )

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        """Удаляет рецепт из избранного."""
        result = get_object_or_404(Recipe, pk=pk)
        favorite = result.favorites.filter(user=request.user)
        return remove_method(favorite)

    @action(
        detail=True, methods=['GET'], url_path='get-link',
        permission_classes=[AllowAny])
    def get_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт."""
        result = get_object_or_404(Recipe, pk=pk)
        return Response(
            {"short-link": request.build_absolute_uri(f"/s/{result.link}/")},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True, methods=['POST'], url_path='shopping_cart',
        permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавляет рецепт в список покупок."""
        return add_method(
            model=Recipe,
            request=request,
            pk=pk,
            serializer_class=AddFavoriteAndShoppingCartSerializer,
            related_field='recipe',
            model_serializer=ShoppingCart
        )

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk=None):
        """Удаляет рецепт из списка покупок."""
        result = get_object_or_404(Recipe, pk=pk)
        basket = result.shoppingcarts.filter(user=request.user)
        return remove_method(basket)

    @action(
        detail=False, methods=['GET'], url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated])
    def download_basket(self, request):
        """Скачивает список покупок."""
        basket = request.user.shoppingcarts.all()
        ingredients = {}

        for result in basket:
            recipe_ingredients = result.recipe.recipeingredients.all()
            for ingredient in recipe_ingredients:
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                amount = ingredient.amount

                if name in ingredients:
                    ingredients[name]['amount'] += amount
                else:
                    ingredients[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount,
                    }

        list_text = "Список покупок:\n"
        for name, value in ingredients.items():
            list_text += (
                f"- {name} ({value['measurement_unit']}) - "
                f"{value['amount']}\n")
        response = HttpResponse(list_text, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="list.txt"'
        return response


@api_view(['GET'])
@permission_classes([AllowAny])
def short_link(request, link):
    """Короткая ссылка."""
    recipe = get_object_or_404(Recipe, link=link)
    return redirect(f'/recipes/{recipe.id}/')
