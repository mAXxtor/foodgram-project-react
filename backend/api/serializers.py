from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import status  # noqa I005
from rest_framework.exceptions import ValidationError  # noqa I005
from rest_framework.serializers import (IntegerField, ModelSerializer,  # noqa I005
                                        PrimaryKeyRelatedField, ReadOnlyField,  # noqa I005
                                        SerializerMethodField,  # noqa I005
                                        UniqueTogetherValidator)  # noqa I005
# noqa I004
from recipes.models import (Cart, Favorite, Ingredient, IngredientInRecipe,  # noqa I001
                            Recipe, Tag)  # noqa I001
from users.models import CustomUser as User  # noqa I001
# noqa I005


class RecipeMinifiedSerializer(ModelSerializer):
    """ Сериализатор для модели Recipe с минимальным набором полей. """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)


class UserSerializer(ModelSerializer):
    """ Сериализатор для модели User. """
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'password',)

    def get_is_subscribed(self, obj):
        """ Проверка подписки пользователя. """
        request = self.context.get('request')
        return (
            request is not None
            and request.user.is_authenticated
            and obj.follower.filter(user=request.user).exists()
        )


class UserSubscribeSerializer(UserSerializer):
    """ Сериализатор для вывода подписок. """
    recipes_count = SerializerMethodField()
    recipes = RecipeMinifiedSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes_count', 'recipes',)
        read_only_fields = ('email', 'username', 'first_name', 'last_name',)

    def validate(self, data):
        """ Проверка дублирования подписки на автора и на свой профиль. """
        author = self.instance
        user = self.context.get('request').user
        if user.follower.filter(author=author).exists():
            raise ValidationError(
                detail='Ошибка подписки. Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail='Ошибка подписки. Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_recipes_count(self, user):
        """ Считает количество рецептов у автора. """
        return user.recipes.count()


class TagSerializer(ModelSerializer):
    """ Сериализатор для вывода тегов. """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        read_only_fields = '__all__',


class IngredientSerializer(ModelSerializer):
    """ Сериализатор для вывода ингридиентов. """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        read_only_fields = '__all__',


class IngredientInRecipeReadSerializer(ModelSerializer):
    """ Сериализатор для просмотра ингридиентов в рецепте. """
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class IngredientInRecipeCreateSerializer(ModelSerializer):
    """ Сериализатор добавления ингридиентов для рецепта. """
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField(write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount',)


class RecipeBaseSerializer(ModelSerializer):
    """ Сериализатор базовый для рецепта. """
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    cooking_time = IntegerField()

    class Meta:
        model = Recipe


class RecipeReadSerializer(RecipeBaseSerializer):
    """ Сериализатор для чтения рецептов. """
    tags = TagSerializer(many=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta(RecipeBaseSerializer.Meta):
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_ingredients(self, recipe):
        """ Получает список ингридиентов для рецепта. """
        ingredients = IngredientInRecipe.objects.filter(recipe=recipe)
        return IngredientInRecipeReadSerializer(ingredients, many=True).data

    def get_is_favorited(self, recipe):
        """ Рецепт в избранном. """
        request = self.context.get('request')
        return (
            request is not None
            and request.user.is_authenticated
            and recipe.favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        """ Рецепт в списке покупок. """
        request = self.context.get('request')
        return (
            request is not None
            and request.user.is_authenticated
            and recipe.carts.filter(user=request.user).exists()
        )


class RecipeCreateSerializer(RecipeBaseSerializer):
    """ Сериализатор для создания, редактирования и удаления рецептов. """
    tags = PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        error_messages={'does_not_exist': 'Указанного тега не существует'}
    )
    ingredients = IngredientInRecipeCreateSerializer(many=True)

    class Meta(RecipeBaseSerializer.Meta):
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image', 'text',
            'cooking_time',
        )

    def validate(self, data):
        """ Проверка входных данных при создании и редактировании рецепта. """
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')

        # валидация Tags
        if not tags:
            raise ValidationError(
                {'tags': 'Требуется добавить тег'})
        tags_list = [None]
        for tag in tags:
            if not Tag.objects.filter(id=tag).exists():
                raise ValidationError({'tags': 'Такого тега не существует'})
            if tag in tags_list:
                raise ValidationError({'tags': 'Тег уже добавлен в рецепт'})
            tags_list.append(tag)

        # валидация Ingredients и Amount
        if not ingredients:
            raise ValidationError(
                {'ingredients': 'Требуется добавить ингридиент'})
        ingredients_list = [None]
        for element in ingredients:
            ingredient = get_object_or_404(Ingredient, id=element['id'])
            if ingredient in ingredients_list:
                raise ValidationError(
                    {'ingredients': 'Ингредиент уже добавлен в рецепт'})
            if int(element.get('amount')) < settings.MIN_INGR_AMOUNT:
                raise ValidationError(
                    'Количество ингредиента должно быть больше 1')
            ingredients_list.append(ingredient)

        # валидация Сooking_time
        if int(data.get('cooking_time')) < settings.MIN_COOKING_TIME:
            raise ValidationError(
                {'cooking_time':
                 'Время приготовления должно быть больше 1 минуты'})
        return data

    @staticmethod
    def create_ingredients(recipe, ingredients):
        """ Создает связи Ingredient и Recipe. """
        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient.pop('id'),
                amount=ingredient.pop('amount')
            ) for ingredient in ingredients
        ]).sort(key=(lambda item: item.ingredient.name), reverse=True)

    def create(self, validated_data):
        """ Создает рецепт. """
        request = self.context.get('request', None)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        if request.user.recipes.filter(
            name=validated_data.get('name')
        ).exists():
            raise ValidationError(
                {'recipe': 'Вы уже добавляли рецепт с таким именем'})
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        """ Редактирует рецепт. """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        if ingredients:
            recipe.ingredients.clear()
            self.create_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        return RecipeReadSerializer(recipe, context={
            'request': self.context.get('request')
        }).data


class FavoriteSerializer(ModelSerializer):
    """ Сериализатор для избранных рецептов. """
    class Meta:
        model = Favorite
        fields = ('recipe', 'user',)
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('recipe', 'user'),
                message='Рецепт уже добавлен в избранное'
            ),
        ]

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class CartSerializer(ModelSerializer):
    """ Сериализатор для списка покупок. """

    class Meta:
        model = Cart
        fields = ('recipe', 'user',)
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('recipe', 'user'),
                message='Рецепт уже добавлен в список покупок'
            ),
        ]

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
