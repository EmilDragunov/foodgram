from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='subscriber',
                             verbose_name='Подписчик')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='subscriptions',
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'author')

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'


User._meta.get_field('first_name').blank = False
User._meta.get_field('last_name').blank = False
User.add_to_class('avatar', models.ImageField(upload_to='avatars/', blank=True,
                                              null=True,
                                              verbose_name='Аватар'))
