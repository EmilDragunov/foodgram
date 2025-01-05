from rest_framework import viewsets
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from .models import Ingredient, Tag, Recipe, Subscription
from .serializers import (IngredientSerializer, TagSerializer,
                          RecipeSerializer, RecipePostSerializer,
                          UserSerializer, SubscriptionSerializer)
from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination

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


class RecipePagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.DjangoFilterBackend,
                       rest_filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering_fields = ('name', 'pub_date')
    pagination_class = RecipePagination

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

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk=None):
        user = request.user
        author = self.get_object()
        if request.method == 'POST':
            if user.subscriber.filter(author=author).exists():
                return Response({'errors': 'Вы уже подписаны на этого автора'},
                                status=status.HTTP_400_BAD_REQUEST)
            user.subscriber.create(author=author)
            return Response({'message': 'Вы подписались на этого автора'},
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if user.subscriber.filter(author=author).exists():
                user.subscriber.filter(author=author).delete()
                return Response({'message': 'Вы отписались от этого автора'},
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Вы не были подписаны на этого автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['PATCH'], detail=True,
            permission_classes=(IsAuthenticated,))
    def set_avatar(self, request, pk=None):
        user = self.get_object()
        serializer = UserSerializer(user, data=request.data, partial=True,
                                    context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True,
            permission_classes=(IsAuthenticated,))
    def recipes(self, request, pk=None):
        user = self.get_object()
        recipes = Recipe.objects.filter(author=user)
        paginator = RecipePagination()
        result_page = paginator.paginate_queryset(recipes, request)
        serializer = RecipeSerializer(result_page, many=True,
                                      context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    @action(methods=['GET'], detail=False,
            permission_classes=(IsAuthenticated,))
    def recipes(self, request):
        user = request.user
        authors = user.subscriber.all().values_list('author', flat=True)
        recipes = Recipe.objects.filter(author__in=authors)
        paginator = RecipePagination()
        result_page = paginator.paginate_queryset(recipes, request)
        serializer = RecipeSerializer(result_page, many=True,
                                      context={'request': request})
        return paginator.get_paginated_response(serializer.data)
