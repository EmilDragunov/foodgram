"""Модели для управления пользователями."""
from django.db import models
from django.contrib.auth.models import AbstractUser
from foodgram_backend.settings import MAX_LENGTH_EMAIL, MAX_LENGTH_USERNAME
from django.core.exceptions import ValidationError
import re

USERNAME_PATTERN = r'^[w.@+-]+$'


class UserProfile(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        unique=True, blank=True, max_length=MAX_LENGTH_EMAIL,
        verbose_name='Электронная почта'
    )
    username = models.CharField(
        max_length=MAX_LENGTH_USERNAME, blank=True, unique=True,
        verbose_name='Имя пользователя',
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

    def clean(self):
        """Переопределяем метод clean для валидации username."""
        errors = []
        if self.username == 'me':
            errors.append(
                'Использование имени "me" в качестве username запрещено'
            )
        if not re.match(USERNAME_PATTERN, self.username):
            errors.append(
                'Может содержать только буквы, цифры и символы @/./+/-/_'
            )
        if errors:
            raise ValidationError(errors)


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
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('subscribed_to')),
                name='prevent_self_subscription',
            )
        ]

    def __str__(self):
        """Строковое отображение объекта."""
        return f'Подписчик {self.user}'
