"""Модели рецептов."""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from foodgram_backend.settings import MAX_LENGTH_USERNAME
import uuid

User = get_user_model()


class PublishedModel(models.Model):
    """Базовая модель."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE, verbose_name='Рецепт')

    class Meta:
        """Мета данные."""

        abstract = True
        ordering = ('user',)


class Ingredient(models.Model):
    """Ингредиент."""

    name = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единица измерения'
    )

    class Meta:
        """Мета данные."""

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]
        ordering = ('name',)

    def __str__(self):
        """Возвращает имя объекта в виде строки."""
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Тег."""

    name = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug',
        help_text=(
            "Slug страницы для URL; разрешены символы латиницы, "
            "цифры, дефис и подчёркивание."
        )
    )

    class Meta:
        """Мета данные."""

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        """Возвращает имя объекта в виде строки."""
        return self.name


class Recipe(models.Model):
    """Рецепт."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    name = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        verbose_name='Название'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(
            1, message='Количество должно быть больше 0')]
    )
    link = models.CharField(
        max_length=10, unique=True, blank=True, null=True,
        verbose_name='Ссылка')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    image = models.ImageField(upload_to='images/', verbose_name='Картинка')
    text = models.TextField(verbose_name='Описание')

    class Meta:
        """Мета данные."""

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('-pub_date',)

    def __str__(self):
        """Возвращает имя объекта в виде строки."""
        return self.name

    def generate_link(self):
        """Генерация ссылки."""
        self.link = uuid.uuid4().hex[:5]
        while Recipe.objects.filter(link=self.link).exists():
            self.link = uuid.uuid4().hex[:5]


class RecipeIngredient(models.Model):
    """Количество ингредиентов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        blank=False
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент')
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(
            1, message='Количество должно быть больше 0')]
    )

    class Meta:
        """Мета данные."""

        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        default_related_name = 'recipeingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        """Возвращает имя объекта в виде строки."""
        return f'{self.ingredient.name}'


class Favorite(PublishedModel):
    """Избранные рецепты."""

    class Meta:
        """Мета данные."""

        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_user_recipe')
        ]

    def __str__(self):
        """Возвращает имя объекта в виде строки."""
        return f'{self.user}'


class ShoppingCart(PublishedModel):
    """Список покупок."""

    class Meta:
        """Мета данные."""

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shoppingcarts'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_user_ShoppingCart')
        ]

    def __str__(self):
        """Возвращает имя объекта в виде строки."""
        return f'{self.user}'
