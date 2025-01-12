"""URL-ы рецептов."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, TagViewSet, RecipeViewSet

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
