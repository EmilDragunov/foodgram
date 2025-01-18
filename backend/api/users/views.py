"""Вьюсеты для работы с пользователями."""
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated, AllowAny)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from api.utils import delete_relation
from api.pagination import RecipePagination
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    UserAvatarSerializer, SubscriptionSerializer, AddFollowSerializer
)

User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    """ViewSet для пользователей."""

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    pagination_class = RecipePagination

    def get_serializer_class(self):
        """Определяет класс сериализатора на основе действия."""
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    @action(
        detail=False, methods=['GET'], url_path='me',
        permission_classes=[IsAuthenticated])
    def user_info(self, request):
        """Получение информации о текущем пользователе."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False, methods=['PUT'], url_path='me/avatar',
        permission_classes=[IsAuthenticated])
    def upload_avatar(self, request):
        """Загрузка аватара пользователя."""
        user = request.user
        serializer = UserAvatarSerializer(
            user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'avatar': user.avatar.url})

    @upload_avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаление аватара пользователя."""
        user = request.user
        user.avatar.delete()
        return Response(
            {"detail": "Аватар успешно удален"},
            status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['GET'], url_path='subscriptions',
        permission_classes=[IsAuthenticated])
    def user_subscription(self, request):
        """Получение списка подписок пользователя."""
        subscribers = request.user.subscriber.annotate(
            recipes_count=Count('subscribed_to__recipes'))
        paginator = self.pagination_class()
        paginated_subscribers = paginator.paginate_queryset(
            subscribers, request)
        serializer = SubscriptionSerializer(
            paginated_subscribers, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=['POST'], url_path='subscribe',
        permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Подписка на пользователя."""
        user_to_subscribe = get_object_or_404(User, pk=pk)
        serializer = AddFollowSerializer(data={
            'subscribed_to': user_to_subscribe.id,
            'user': request.user.id
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @subscribe.mapping.delete
    def subscribe_delete(self, request, pk=None):
        """Отписка от пользователя."""
        user_to_unsubscribe = get_object_or_404(User, pk=pk)
        subscription = request.user.subscriber.filter(
            subscribed_to=user_to_unsubscribe)
        return delete_relation(subscription)
