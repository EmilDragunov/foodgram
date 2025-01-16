"""Утилиты для API."""
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from recipes.models import RecipeIngredient


def add_method(
    model, request, pk, serializer_class,
    related_field, model_serializer
):
    """Добавление в базу."""
    result = get_object_or_404(model, pk=pk)
    data = {
        'user': request.user.id,
        related_field: result.id
    }
    serializer = serializer_class(data=data, model=model_serializer)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


def remove_method(result_delet):
    """Метод для удаления из базы."""
    if result_delet.exists():
        result_delet.delete()
        return Response(
            {"detail": "Успешно."},
            status=status.HTTP_200_OK)
    return Response(
        {"detail": "Нет такой записи."},
        status=status.HTTP_400_BAD_REQUEST)


def recipe_create_and_update(recipe, ingredients_data, tags_data):
    """Создание и обновление рецепта."""
    if not recipe.link:
        recipe.generate_link()
        recipe.save()
    if tags_data:
        recipe.tags.set(tags_data)
    if ingredients_data:
        recipe.recipeingredients.all().delete()
        ingredients_list = [
            RecipeIngredient(
                recipe=recipe, ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        ]
        recipe.recipeingredients.bulk_create(ingredients_list)
