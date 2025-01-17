"""Админ-панель для пользователей."""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Subscription

User = get_user_model()


@admin.register(User)
class UserProfileAdmin(UserAdmin):
    """Админ-панель для кастомной модели пользователя."""

    list_display = ('pk', 'username', 'display_avatar')
    search_fields = ('email', 'username')
    list_display_links = ('username',)

    @admin.display(description='Аватар пользователя')
    def display_avatar(self, obj):
        """Отображает превью аватара пользователя."""
        if obj.avatar:
            return format_html(
                '<img src="{}" alt="User Avatar" '
                'style="max-height: 100px; max-width: 100px;"/>',
                obj.avatar.url
            )
        return 'Нет изображения'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админ-панель для подписок пользователей."""

    list_display = ('user', 'subscribed_to')
