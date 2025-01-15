"""Модели для управления пользователями."""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from foodgram_backend.settings import MAX_LENGTH_EMAIL, MAX_LENGTH_USERNAME


class UserProfile(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        unique=True, blank=True, max_length=MAX_LENGTH_EMAIL,
        verbose_name='Электронная почта'
    )
    username = models.CharField(
        max_length=MAX_LENGTH_USERNAME, blank=True, unique=True,
        verbose_name='Имя пользователя',
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message=(
                    'Имя пользователя может содержать только латинские '
                    'буквы, цифры и символ подчеркивания.'
                ),
                code='invalid_username'
            )
        ]
    )
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        blank=True,
        default=None
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        """Мета данные."""

        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'профили пользователей'
        ordering = ('username',)

    def __str__(self):
        """Строковое отображение объекта."""
        return self.username


class Subscription(models.Model):
    """Модель для подписок."""

    subscribed_to = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
        verbose_name='Подписан на',
    )
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )

    class Meta:
        """Мета данные."""

        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribed_to'],
                name='unique_subscriber_subscription'
            )
        ]

    def clean(self):
        """Метод для проверки."""
        if self.user == self.subscribed_to:
            raise ValidationError('Нельзя подписаться на самого себя.')

    def __str__(self):
        """Строковое отображение объекта."""
        return f'Подписчик {self.user}'
