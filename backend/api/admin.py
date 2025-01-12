from django.contrib import admin
from .models import Ingredient, Tag, Recipe, RecipeIngredient
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


User = get_user_model()


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('email', 'username')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
