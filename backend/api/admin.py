from django.contrib import admin
from .models import Ingredient, Tag, Recipe, RecipeIngredient
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


User = get_user_model()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('author__username', 'name', 'tags__name')
    filter_horizontal = ('tags',)
    list_filter = ('tags', 'author')
    inlines = (RecipeIngredientInline,)

    @admin.display(description='Добавлено в избранное')
    def favorites_count(self, obj):
        return obj.favorites.count()


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('email', 'username')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
