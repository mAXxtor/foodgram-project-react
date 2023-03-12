from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (Cart, Favorite, Ingredient, IngredientInRecipe,
                            Recipe, Tag)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Follow

from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPagination
from .permissions import AuthorOrReadOnly
from .serializers import (CartSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeReadSerializer, TagSerializer,
                          UserSubscribeSerializer)

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """ Список пользователей и редактирование. """
    pagination_class = LimitPagination

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        """ Подписаться или отписаться от пользователя. """
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            serializer = UserSubscribeSerializer(
                author, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(author=author, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        get_object_or_404(Follow, author=author, user=user).delete()
        return Response({'detail': 'Успешная отписка'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """ Подписки пользователя. """
        serializer = UserSubscribeSerializer(
            self.paginate_queryset(
                User.objects.filter(following__user=request.user)),
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """ Список тегов. """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """ Список ингредиентов. """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """ Список рецептов. """
    queryset = Recipe.objects.select_related('author')
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = LimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """ Выбор сериализатора для метода. """
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @staticmethod
    def get_shopping_list(ingredients):
        """ Формирует txt файл со списком покупок и дублирует в сообщении."""
        shopping_list = 'Список покупок:'
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredients__name']} - "
                f"{ingredient['amount']} "
                f"{ingredient['ingredients__measurement_unit']}"
            )
        shopping_list.append('\nFoodgram - продуктовый помощник ')
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list,
                                content_type='text/plain,charset=utf8')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response

    @action(
            detail=False,
            methods=['GET'],
            permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """ Скачивает список покупок. """
        ingredients = IngredientInRecipe.objects.filter(
            recipe__carts__user=request.user
        ).order_by('ingredients__name').values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return self.get_shopping_list(ingredients)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """ Добавляет рецепт в список покупок. """
        data = {
            'recipe': get_object_or_404(Recipe, id=pk).id,
            'user': request.user.id
        }
        serializer = CartSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def del_from_shopping_cart(self, request, pk):
        """ Удаляет рецепт из списка покупок. """
        cart = Cart.objects.filter(
            user=request.user, recipe=get_object_or_404(Recipe, id=pk))
        if not cart.exists():
            return Response(
                {'errors': 'Рецепт не был добавлен в список покупок'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """ Добавляет в список избранных рецептов. """
        data = {
            'recipe': get_object_or_404(Recipe, id=pk).id,
            'user': request.user.id
        }
        serializer = FavoriteSerializer(data=data,
                                        context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def del_from_favorite(self, request, pk):
        """ Удаляет из списка избранных рецептов. """
        favorite = Favorite.objects.filter(
            user=request.user, recipe=get_object_or_404(Recipe, id=pk))
        if not favorite.exists():
            return Response(
                {'errors': 'Рецепт не был добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
