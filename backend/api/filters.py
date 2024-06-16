from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import (BooleanFilter, CharFilter,
                                                   ModelMultipleChoiceFilter,
                                                   NumberFilter)
from recipes.models import Ingredients, Recipe, Tag


class IngredientFilter(FilterSet):
    """Фильтр для поиска ингредиентов по названию"""
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredients
        fields = ('name', 'measurement_unit')


class RecipeFilter(FilterSet):
    """"Фильтр для поиска и фильтрации рецептов по названию, автору и тегам"""
    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    author = NumberFilter(field_name='author__id')
    is_favorited = BooleanFilter(method='get_favorite_filter')
    is_in_shopping_cart = BooleanFilter(method='get_shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def get_favorite_filter(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset.none()

    def get_shopping_cart_filter(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
