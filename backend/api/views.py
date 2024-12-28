from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Ingredient, Tag, Recipe
from .serializers import (IngredientSerializer, TagSerializer,
                          RecipeSerializer, RecipePostSerializer)
from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model


User = get_user_model()


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


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


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (
        filters.DjangoFilterBackend,
        rest_filters.OrderingFilter
    )
    filterset_class = RecipeFilter
    ordering_fields = ('name',)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipePostSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@action(methods=['POST', 'DELETE'], detail=True,
        permission_classes=(AllowAny,))
def favorite(self, request, pk=None):
    user = request.user
    recipe = self.get_object()
    if request.method == 'POST':
        if user.favorites.filter(recipe=recipe).exists():
            return Response({'errors': 'Рецепт уже в избранном'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        user.favorites.create(recipe=recipe)
        return Response({'message': 'Рецепт добавлен в избранное'},
                        status=status.HTTP_201_CREATED
                        )
    if request.method == 'DELETE':
        if user.favorites.filter(recipe=recipe).exists():
            user.favorites.filter(recipe=recipe).delete()
            return Response({'message': 'Рецепт удалён из избранного'},
                            status=status.HTTP_204_NO_CONTENT
                            )
        return Response({'errors': 'Рецепт не был добавлен в избранное'},
                        status=status.HTTP_400_BAD_REQUEST
                        )
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@action(methods=['POST', 'DELETE'], detail=True,
        permission_classes=(AllowAny,))
def shopping_cart(self, request, pk=None):
    user = request.user
    recipe = self.get_object()
    if request.method == 'POST':
        if user.shopping_cart.filter(recipe=recipe).exists():
            return Response({'errors': 'Рецепт уже в списке покупок'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        user.shopping_cart.create(recipe=recipe)
        return Response({'message': 'Рецепт добавлен в список покупок'},
                        status=status.HTTP_201_CREATED
                        )
    if request.method == 'DELETE':
        if user.shopping_cart.filter(recipe=recipe).exists():
            user.shopping_cart.filter(recipe=recipe).delete()
            return Response({'message': 'Рецепт удалён из списка покупок'},
                            status=status.HTTP_204_NO_CONTENT
                            )
        return Response({'errors': 'Рецепт не был добавлен в список покупок'},
                        status=status.HTTP_400_BAD_REQUEST
                        )
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@action(methods=['GET'], detail=False, permission_classes=(AllowAny,))
def download_shopping_cart(self, request):
    user = request.user
    ingredients = {}
    recipes = user.shopping_cart.all()
    for recipe in recipes:
        for ingredient in recipe.recipe.ingredients.all():
            if ingredient.name in ingredients:
                ingredients[ingredient.name]['amount'] += recipe.amount
            else:
                ingredients[ingredient.name] = {'amount': recipe.amount,
                                                'unit':
                                                ingredient.measurement_unit
                                                }

    result = ''
    for key, value in ingredients.items():
        result += f'{key} {value["amount"]} {value["unit"]}\n'
    response = Response(result, content_type='text/plain',
                        status=status.HTTP_200_OK
                        )
    response['Content-Disposition'
             ] = 'attachment; filename="shopping_cart.txt"'
    return response
