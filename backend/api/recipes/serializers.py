"""Сериализаторы для рецептов."""
from rest_framework import serializers
from recipes.models import Ingredient, Tag, Recipe, RecipeIngredient
from django.contrib.auth import get_user_model
from api.users.serializers import UserSerializer


User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода ингредиентов."""

    class Meta:
        """Мета."""

        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода тегов."""

    class Meta:
        """Мета."""

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
        """Мета."""

        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецептов."""

    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipeingredient_set')
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Мета."""

        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()





class RecipePostSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField()
    tags = serializers.ListField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingr in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingr['id'])
            RecipeIngredient.objects.create(recipe=recipe,
                                            ingredient=ingredient,
                                            amount=ingr['amount'])
        for tag_id in tags_data:
            tag = Tag.objects.get(id=tag_id)
            recipe.tags.add(tag)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)

        if ingredients_data:
            instance.ingredients.clear()
            for ingr in ingredients_data:
                ingredient = Ingredient.objects.get(id=ingr['id'])
                RecipeIngredient.objects.create(recipe=instance,
                                                ingredient=ingredient,
                                                amount=ingr['amount'])

        if tags_data:
            instance.tags.clear()
            for tag_id in tags_data:
                tag = Tag.objects.get(id=tag_id)
                instance.tags.add(tag)

        instance.save()
        return instance
