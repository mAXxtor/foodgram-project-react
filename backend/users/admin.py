""" Модуль для администрирования приложения `users`. """
from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name',
                    'count_recipes', 'count_following')
    search_fields = ('email', 'username',)
    list_filter = ('email', 'username',)
    ordering = ('username',)

    @admin.display(description='Количество рецептов')
    def count_recipes(self, user):
        """ Считает количество рецептов у пользователя. """
        return user.recipes.count()

    @admin.display(description='Количество подписчиков')
    def count_following(self, author):
        """ Считает количество подписчиков у пользователя. """
        return author.following.count()
