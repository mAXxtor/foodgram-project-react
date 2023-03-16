from django.db.models import IntegerField, Value
from django_filters.rest_framework import (BooleanFilter, CharFilter,
                                           FilterSet, filters)
from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    """ Фильтр для Recipe. """
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')
    is_favorited = BooleanFilter(method='get_is_favorited')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ('author',)

    def get_is_in_shopping_cart(self, queryset, name, value):
        """ Queryset для рецептов в списке покупок. """
        if value and self.request.user.is_authenticated:
            return queryset.filter(carts__user=self.request.user)
        return None

    def get_is_favorited(self, queryset, name, value):
        """ Queryset для избранных рецептов. """
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset


# Из за ограничений SQlite не поддерживается order_by в связке
# с union в субзапросах
# https://stackoverflow.com/questions/65577792/error-order-by-not-allowed-in-subqueries-of-compound-statements-in-django-whi
# Получилось победить убрав сортировку в модели Ingredient
# На PostgreSQL фильтр работает с сортировкой в Модели.
class IngredientFilter(FilterSet):
    """ Фильтр для Ingredient.
        Поиск по полю name регистронезависимо:
            по вхождению в начало названия,
            по вхождению в произвольном месте.
        Сортировка от первых ко вторым.
    """
    name = CharFilter(method='search_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def search_name(self, queryset, name, value):
        """ Поиск по имени Ingredient. """
        if not value:
            return queryset
        starts_with_queryset = (
            queryset.filter(name__istartswith=value).annotate(
                order=Value(0, IntegerField())
            )
        )
        contain_queryset = (
            queryset.filter(name__icontains=value).exclude(
                pk__in=(ingredient.pk for ingredient in starts_with_queryset)
            ).annotate(
                order=Value(1, IntegerField())
            )
        )
        return starts_with_queryset.union(contain_queryset).order_by('order')
