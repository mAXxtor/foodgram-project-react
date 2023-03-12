""" Модуль для администрирования приложения `users`. """
from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name',)
    search_fields = ('email', 'username',)
    list_filter = ('email', 'username',)
    ordering = ('username',)
