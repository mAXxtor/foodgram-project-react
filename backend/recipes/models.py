""" Модели приложения `recipes`.

Models:
    Ingredient:
        Модель описания ингредиентов.
        Связана с Recipe через модель IngredientInRecept (ManyToMany).
    Tag:
       Модель описания тэгов для группировки и сортировки рецептов.
       Связана с Recipe (ManyToMany).
    Recipe:
        Основная модель, описывающая рецепты.
    IngredientInRecept:
        Модель для связи Recipe и Ingredient с указанием количества
        ингредиентов.
    Favorite:
        Модель для связи Recipe и User. Определяет избранные рецепты
        для пользователя.
    Cart:
        Модель для связи Recipe и User. Определяет рецепты в списке покупок
        пользователя.
"""
from colorfield.fields import ColorField
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Ingredient(models.Model):
    """ Ингредиент для рецептов.

    Attributes:
        name(str):
            Название ингредиента.
            Ограничение по длине (200).
        measurement_unit(str):
            Единица измерения ингредента.
            Ограничение по длине (200).
    """
    name = models.CharField(
        'Название ингредиента',
        max_length=settings.MAX_LEN_MODEL_FIELD,
    )
    measurement_unit = models.CharField(
        'Единица измерения ингредиента',
        max_length=settings.MAX_LEN_MODEL_FIELD,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        # ordering = ('name',) Закомментировал из-за проблем
        # с SQlite по фильтрации
        constraints = [models.UniqueConstraint(fields=[
            'name', 'measurement_unit'], name='unique_unit_for_ingredient')
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    """ Тег для рецептов.

    Attributes:
        name(str):
            Название тега рецепта.
            Ограничение по длине (200), уникальные.
        color(str):
            Цвет тега в HEX.
            Ограничение по длине (7), уникальные.
        slug(str):
            Слаг тега рецепта.
            Ограничение по длине (200), уникальные.
    """
    name = models.CharField(
        'Название тега',
        max_length=settings.MAX_LEN_MODEL_FIELD,
        db_index=True,
        unique=True,
    )
    color = ColorField(
        'Цвет тега в HEX',
        format='hex',
        max_length=settings.MAX_LEN_HEX_FIELD,
        unique=True,
    )
    slug = models.SlugField(
        'Slug тега',
        max_length=settings.MAX_LEN_MODEL_FIELD,
        db_index=True,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} (цвет: {self.color})'


class Recipe(models.Model):
    """ Рецепты.

    Attributes:
        author(int):
            Автор рецепта.
            Связь ForeignKey с моделью User.
        name(str):
            Название рецепта.
            Ограничение по длине (200).
        image(str):
            Изображение рецепта.
            Ссылка (url) на изображение.
        text(str):
            Описание рецепта.
        ingredients(int):
            Ингредиенты для рецепта.
            Связь ManyToMany с моделью Ingredient через
            модель IngredientInRecept.
        tags(array[int]):
            Список тегов рецепта.
            Связь ManyToMany с моделью Tag.
        cooking_time(int):
            Время приготовления рецепта.
            Ограничение по минимальному значению (1).
    """
    author = models.ForeignKey(
        verbose_name='Автор рецепта',
        related_name='recipes',
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    name = models.CharField(
        'Название рецепта',
        max_length=settings.MAX_LEN_MODEL_FIELD,
    )
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='recipes/',
    )
    text = models.TextField(
        'Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        verbose_name='Ингредиенты для рецепта',
        related_name='recipes',
        to=Ingredient,
        through='IngredientInRecipe',
    )
    tags = models.ManyToManyField(
        verbose_name='Тег рецепта',
        related_name='recipes',
        to=Tag,
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления по рецепту',
        validators=(MinValueValidator(settings.MIN_COOKING_TIME),),
        error_messages={'validators':
                        'Минимальное время приготовления 1 минута'},
        default=1,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)
        constraints = [models.UniqueConstraint(fields=[
            'name', 'author'], name='unique_recipe_for_author')
        ]

    def ingredients_list(self):
        return ' %s' % (', '.join(
            [ingredient.name for ingredient in self.ingredients.all()]))
    ingredients_list.short_description = 'Список ингредиентов'

    def __str__(self):
        return f'{self.name} (Автор: {self.author.username})'


class IngredientInRecipe(models.Model):
    """ Количество ингредиентов в рецепте.
    Связь моделей Recipe и Ingredient с указанием количества ингредиентов.

    Attributes:
        recipe(int):
            Рецепт.
            Связь ForeignKey с моделью Recipe.
        ingredients(int):
            Ингредиент.
            Связь ForeignKey с моделью Ingredient.
        amount(int):
            Количиство ингредиентов в рецепте.
            Ограничение по минимальному значению (1).
    """
    recipe = models.ForeignKey(
        verbose_name='Связанный рецепт',
        related_name='ingredient',
        to=Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        verbose_name='Связанные ингредиенты',
        related_name='recipe',
        to=Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиентов',
        validators=(MinValueValidator(settings.MIN_INGR_AMOUNT),),
        error_messages={'validators':
                        'В рецепте должен быть как минимум 1 ингредиент'}
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('-id', )
        constraints = [models.UniqueConstraint(fields=[
            'recipe', 'ingredient'], name='unique_ingredient_in_recipe')
        ]

    def __str__(self):
        return f'{self.amount} {self.ingredient} в {self.recipe}'


class FavoriteCartAbstractModel(models.Model):
    """ Абстрактная модель для Favorite и Cart. """
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        ordering = ('recipe',)

    def __str__(self):
        return f'{self.recipe} в списке {self.user}'


class Favorite(FavoriteCartAbstractModel):
    """ Избранные рецепты.
    Связь моделей Recipe и User.

    Attributes:
        recipe(int):
            Рецепт.
            Связь ForeignKey с моделью Recipe.
        user(int):
            Пользователь.
            Связь ForeignKey с моделью User.
    """
    class Meta(FavoriteCartAbstractModel.Meta):
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_recipe_in_favorites')
        ]


class Cart(FavoriteCartAbstractModel):
    """ Список покупок.
    Связь моделей Recipe и User.

    Attributes:
        recipe(int):
            Рецепт.
            Связь ForeignKey с моделью Recipe.
        user(int):
            Пользователь.
            Связь ForeignKey с моделью User.
        add_date(datetime):
            Дата добавления в список покупок.
    """
    class Meta(FavoriteCartAbstractModel.Meta):
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        default_related_name = 'carts'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_recipe_in_cart')
        ]
