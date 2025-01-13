"""Вьюсеты для пользователей."""
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated, AllowAny)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from api.utils import add_method, remove_method
from api.pagination import RecipePagination
from .serializers import (
    UserSerializer, RegistrationSerializer, UserAvatarSerializer,
    FollowSerializer, AddFollowSerializer)
from users.models import Follow


User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    """Пользователи"""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.action == 'create':
            return RegistrationSerializer
        return UserSerializer

    @action(
        detail=False, methods=['get'], url_path='me',
        permission_classes=[IsAuthenticated])
    def user_information(self, request):
        """users/me"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False, methods=['put'], url_path='me/avatar',
        permission_classes=[IsAuthenticated])
    def avatar(self, request):
        """Добавить аватар пользователя"""
        user = request.user
        serializer = UserAvatarSerializer(
            user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'avatar': user.avatar.url})

    @avatar.mapping.delete
    def avatar_delete(self, request):
        """Удалить аватар пользователя"""
        user = request.user
        user.avatar.delete()
        return Response(
            {"detail": "Аватар успешно удален"},
            status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['get'], url_path='subscriptions',
        permission_classes=[IsAuthenticated])
    def user_follow(self, request):
        """Список подписок"""
        follows = request.user.follower.annotate(
            recipes_count=Count('following__recipes'))
        paginator = self.pagination_class()
        paginated_follows = paginator.paginate_queryset(follows, request)
        serializer = FollowSerializer(
            paginated_follows, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=['post'], url_path='subscribe',
        permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Подписаться на пользователя"""
        return add_method(
            model=User,
            request=request,
            pk=pk,
            serializer_class=AddFollowSerializer,
            related_field='following',
            model_serializer=Follow
        )

    @subscribe.mapping.delete
    def subscribe_delete(self, request, pk=None):
        """Отписаться от пользователя"""
        result = get_object_or_404(User, pk=pk)
        follow = request.user.follower.filter(following=result)
        return remove_method(follow)
