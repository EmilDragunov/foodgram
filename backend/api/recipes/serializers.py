"""Сериализаторы для рецептов."""
from rest_framework import serializers
from recipes.models import Ingredient, Tag, Recipe, RecipeIngredient
from django.contrib.auth import get_user_model
from api.users.serializers import UserSerializer
from api.utils import recipe_create_and_update
from drf_extra_fields.fields import Base64ImageField


User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода ингредиентов."""

    class Meta:
        """Мета данные."""

        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода тегов."""

    class Meta:
        """Мета данные."""

        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов и количества."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        """Мета данные."""

        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецептов."""

    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = serializers.ImageField()

    class Meta:
        """Мета данные."""

        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        """Проверяет, находится ли рецепт в избранном пользователя."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, находится ли рецепт в списке покупок пользователя."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.shoppingcarts.filter(recipe=obj).exists()

    def get_ingredients(self, obj):
        """Получает ингредиенты рецепта."""
        result = obj.recipeingredients.all()
        return RecipeIngredientSerializer(result, many=True).data


class AddRecipeIngredientSerializer(serializers.Serializer):
    """Сериализатор для добавления ингредиента к рецепту."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)


class AddRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    ingredients = AddRecipeIngredientSerializer(
        many=True, min_length=2, error_messages={
            "min_length":
            "Список ингредиентов не должен быть пустым или быть больше 1."
        })
    image = Base64ImageField()

    class Meta:
        """Мета данные."""

        model = Recipe
        fields = [
            'ingredients', 'tags', 'image', 'name', 'text', 'name',
            'cooking_time', 'link']

    def validate_image(self, value):
        """Проверяет, что поле image не пустое."""
        if not value:
            raise serializers.ValidationError(
                "Не может быть пустым.")
        return value

    def validate_ingredients(self, value):
        """Проверяет, что ингредиенты не дублируются."""
        ingredient_ids = {ingredient['id'] for ingredient in value}
        if len(value) > len(ingredient_ids):
            raise serializers.ValidationError(
                "Не может быть одинаковых игридиентов")
        return value

    def to_representation(self, instance):
        """Возвращает сериализованные данные рецепта."""
        recipe_serializer = RecipeSerializer(instance, context=self.context)
        return recipe_serializer.data

    def create(self, validated_data):
        """Создает новый рецепт."""
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)
        recipe = super().create(validated_data)
        recipe_create_and_update(recipe, ingredients_data, tags_data)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт."""
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)
        recipe = super().update(instance, validated_data)
        recipe_create_and_update(recipe, ingredients_data, tags_data)
        return instance


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сокращенный сериализатор для рецептов."""

    class Meta:
        """Мета данные."""

        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class AddFavoriteAndShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в избранное и список покупок."""

    class Meta:
        """Мета данные."""

        model = None
        fields = ['user', 'recipe']

    def __init__(self, *args, **kwargs):
        """Инициализация."""
        self.Meta.model = kwargs.pop('model')
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        """Возвращает сокращенные данные рецепта."""
        serializer = RecipeShortSerializer(instance.recipe)
        return serializer.data
