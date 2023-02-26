""" Модуль для администрирования приложения `recipes`. """
from django.contrib import admin

from .models import Cart, Favorite, Ingredient, IngredientInRecept, Recipe, Tag


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """ Управление ингридиентами """
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """ Управление тегами """
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name', 'slug',)
    list_filter = ('name',)
    list_editable = ('slug')


class IngredientInLine(admin.TabularInline):
    model = IngredientInRecept
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """ Управление рецептами """
    list_display = (
        'author', 'name', 'cooking_time', 'slug', 'count_favorites',
    )
    search_fields = ('name', 'slug',)
    list_filter = ('name', 'author', 'tags',)
    inlines = (IngredientInLine,)

    @admin.display(description='Добавлено в избранное')
    def count_favorites(self, obj):
        """ Общее число добавлений рецепта в избранное """
        return obj.favorites.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """ Управление избранным """
    list_display = ('recipe', 'user', 'add_date',)
    search_fields = ('recipe ', 'user',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """ Управление корзиной """
    list_display = ('recipe', 'user', 'add_date',)
    search_fields = ('recipe ', 'user',)
