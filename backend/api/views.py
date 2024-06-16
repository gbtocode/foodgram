from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.constants import SHOPPING_CART_FILENAME
from recipes.models import (Favorites, IngredientAmount, Ingredients, Recipe,
                            ShoppingCart, Tag)
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated

from .filters import IngredientFilter, RecipeFilter
from .paginators import CustomPagination
from .permissions import IsAuthorOrReadOnlyOrAuthenticated
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeReadSerializer, TagSerializer)
from .utils import object_create, object_delete

User = get_user_model()


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с тегами"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами"""
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('^name',)
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами """
    pagination_class = CustomPagination
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnlyOrAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.with_favorites_and_shopping_cart(user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(
        methods=['POST'],
        permission_classes=(IsAuthenticated,), detail=True
    )
    def favorite(self, request, pk):
        user = request.user
        model = Favorites
        return object_create(user, model, pk=pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        user = request.user
        model = Favorites
        return object_delete(user, model, pk=pk)

    @action(
        methods=['POST'],
        permission_classes=(IsAuthenticated,), detail=True
    )
    def shopping_cart(self, request, pk):
        user = request.user
        model = ShoppingCart
        return object_create(user, model, pk=pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        user = request.user
        model = ShoppingCart
        return object_delete(user, model, pk=pk)

    @action(
        methods=['GET'],
        permission_classes=(IsAuthenticated,), detail=False
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=request.user).values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(total=Sum('amount'))

        shopping_cart = '\n'.join([
            f'{ingredient["ingredient__name"]} - {ingredient["total"]} '
            f'{ingredient["ingredient__measurement_unit"]}'
            for ingredient in ingredients
        ])
        filename = SHOPPING_CART_FILENAME
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
