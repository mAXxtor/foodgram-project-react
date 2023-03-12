""" Модель пользователя и подписок. """
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class CustomUser(AbstractUser):
    """Модель пользователя.
    Все поля обязательны.

    Attributes:
        email(str):
            Адрес электронной почты.
            Ограничение по максимальной длине (254).
        username(str):
            Юзернейм пользователя.
            Уникален. Ограничение по максимальной длине (150).
        first_name(str):
            Имя пользователя.
            Ограничение по максимальной длине (150).
        last_name(str):
            Фамилия пользователя.
            Ограничение по максимальной длине (150).
        password(str):
            Пароль.
            Ограничение по максимальной длине (150)
        is_active (bool):
            Активен или заблокирован пользователь.
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=settings.MAX_LEN_EMAIL,
        help_text='Укажите email',
        unique=True,
    )
    username = models.CharField(
        verbose_name='Логин',
        max_length=settings.MAX_LEN_USER_ATTR,
        help_text='Укажите логин',
        unique=True,
        validators=(validate_username,),
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.MAX_LEN_USER_ATTR,
        help_text='Укажите Имя',
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.MAX_LEN_USER_ATTR,
        help_text='Укажите Фамилию',
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=settings.MAX_LEN_USER_ATTR,
        help_text='Укажите пароль',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'{self.username} (email: {self.email})'


class Follow(models.Model):
    """ Модель подписки пользователя на автора.

        Attributes:
            author(int):
                Автор рецепта.
            user(int):
                Подписчик на автора.
    """
    author = models.ForeignKey(
        verbose_name='Автор рецептов',
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
    )
    user = models.ForeignKey(
        verbose_name='Подписчик',
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'user',),
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='no_self_follow'
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} подписан на {self.author}"
