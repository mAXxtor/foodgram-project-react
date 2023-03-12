from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Cart, Favorite, Ingredient, IngredientInRecipe,
                            Recipe, Tag)
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField,
                                        UniqueTogetherValidator)

User = get_user_model()


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
        if request.user.is_anonymous or (request.user == obj):
            return False
        return obj.follower.filter(user=request.user).exists()

    def create(self, validated_data):
        """ Создание нового пользователя. """
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


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


class IngredientInRecipeSerializer(ModelSerializer):
    """ Сериализатор связи ингридиентов и рецепта """
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeBaseSerializer(ModelSerializer):
    """ Сериализатор базовый для рецепта. """
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    cooking_time = IntegerField()

    class Meta:
        model = Recipe


class RecipeReadSerializer(RecipeBaseSerializer):
    """ Сериализатор для чтения рецептов. """
    tags = SerializerMethodField()
    ingredients = IngredientInRecipeSerializer(many=True, source='ingredient')
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta(RecipeBaseSerializer.Meta):
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_tags(self, recipe):
        """ Получает список тегов для рецепта. """
        return TagSerializer(
            Tag.objects.filter(recipes=recipe),
            many=True,
        ).data

    def get_ingredients(self, recipe):
        """ Получает список ингридиентов для рецепта. """
        ingredients = recipe.ingredients.filter(recipe=recipe)
        return IngredientInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, recipe):
        """ Рецепт в избранном. """
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        """ Рецепт в списке покупок. """
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.carts.filter(recipe=recipe).exists()


class RecipeCreateSerializer(RecipeBaseSerializer):
    """ Сериализатор для создания, редактирования и удаления рецептов. """
    tags = PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        error_messages={'does_not_exist': 'Указанного тега не существует'}
    )
    ingredients = IngredientInRecipeSerializer(many=True)

    class Meta(RecipeBaseSerializer.Meta):
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image', 'text',
            'cooking_time',
        )

    def validate(self, data):
        """ Проверка входных данных при создании и редактировании рецепта. """
        user = self.context.get('request').user
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        if not tags or not ingredients:
            raise ValidationError('Недостаточно данных для публикации рецепта')
        for tag in tags:
            if not Tag.objects.filter(id=tag).exists():
                raise ValidationError('Такого тега не существует')
        ingredients_list = [None] * len(ingredients)
        for element in ingredients:
            ingredient = get_object_or_404(Ingredient, id=element['id'])
            if ingredient in ingredients_list:
                raise ValidationError('Ингредиент уже добавлен в рецепт')
            if int(element.get('amount')) < settings.MIN_INGR_AMOUNT:
                raise ValidationError(
                    'Количество ингредиента должно быть больше 1')
            ingredients_list.append(ingredient)
        if user.recipes.filter(name=self.initial_data.get('name')).exists():
            raise ValidationError('Автор уже добавлял рецепт с таким именем')
        return data

    @staticmethod
    def create_ingredients(recipe, ingredients):
        """ Создает связи Ingredient и Recipe. """
        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredients=ingredient.pop('id'),
                amount=ingredient.pop('amount')
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        """ Создает рецепт. """
        request = self.context.get('request', None)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
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
