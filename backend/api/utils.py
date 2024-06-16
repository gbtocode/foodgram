from api.serializers import MiniRecipeSerializer
from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import status
from rest_framework.response import Response


def object_create(user, model, pk):
    """Общий метод для добавления рецепта в избранное и корзину"""
    try:
        recipe = Recipe.objects.get(id=pk)
    except Recipe.DoesNotExist:
        return Response(
            'Такого рецепта не существует',
            status=status.HTTP_400_BAD_REQUEST
        )
    if model.objects.filter(user=user, recipe=recipe).exists():
        return Response(
            'Рецепт уже добавлен',
            status=status.HTTP_400_BAD_REQUEST
        )
    model.objects.create(user=user, recipe=recipe)
    serializer = MiniRecipeSerializer(recipe)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def object_delete(user, model, pk):
    """Общий метод для удаления рецепта из избранного и корзины"""
    get_object_or_404(Recipe, id=pk)
    obj = model.objects.filter(user=user, recipe__id=pk).first()
    if obj is None:
        return Response(
            'Рецепт удалён',
            status=status.HTTP_400_BAD_REQUEST
        )
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
