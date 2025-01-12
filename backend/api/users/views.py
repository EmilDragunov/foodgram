"""Вьюсеты для пользователей."""
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
from api.pagination import RecipePagination


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Пользователи."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    pagination_class = RecipePagination

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
