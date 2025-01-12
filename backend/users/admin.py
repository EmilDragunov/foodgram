"""Админ-зона пользователя."""
from django.contrib import admin
from .models import Follow
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


User = get_user_model()


@admin.register(User)
class UserProfileAdmin(UserAdmin):
    """Пользователь."""

    list_display = ('pk', 'username', 'image_preview')
    search_fields = ('email', 'username')
    list_display_links = ('username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Подписки пользователей."""

    list_display = ('user', 'following',)
