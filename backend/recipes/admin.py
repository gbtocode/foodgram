from django.contrib import admin

from .models import (Favorites, IngredientAmount, Ingredients, Recipe,
                     ShoppingCart, Tag)


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'id',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'amount', 'ingredient',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Favorites, FavoritesAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
