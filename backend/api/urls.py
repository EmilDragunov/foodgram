from django.urls import include, path
from rest_framework import routers
from .views import (IngredientViewSet, TagViewSet,
                    RecipeViewSet, UserViewSet, SubscriptionViewSet)

router = routers.DefaultRouter()
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'users', UserViewSet)
router.register(r'subscriptions', SubscriptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
