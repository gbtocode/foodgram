from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef
from recipes.constants import (MAX_CHAR_LENGTH_254, MAX_COLOR_LENGTH,
                               MAX_LENGTH_200, MEASUREMENT_UNITS_LENGTH)
from users.models import User


class Tag(models.Model):
    """Модель тегов"""
    name = models.CharField(
        max_length=MAX_LENGTH_200,
        verbose_name='Название тега',
        unique=True,
    )
    color = ColorField(
        verbose_name='Цветовой код HEX-формата',
        max_length=MAX_COLOR_LENGTH,
    )
    slug = models.CharField(
        max_length=MAX_LENGTH_200,
        verbose_name='Слаг',
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=MAX_CHAR_LENGTH_254,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MEASUREMENT_UNITS_LENGTH,
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingr_name_and_unit',
            ),
        )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class RecipeQuerySet(models.QuerySet):
    def with_favorites_and_shopping_cart(self, user):
        return self.prefetch_related('tags', 'ingredients').annotate(
            is_favorited=Exists(Favorites.objects.filter(
                user=user,
                recipe=OuterRef('pk')
            )),
            is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                user=user,
                recipe=OuterRef('pk')
            ))
        )


class Recipe(models.Model):
    """Модель рецептов"""
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True,
    )
    name = models.CharField(
        max_length=MAX_LENGTH_200,
        verbose_name='Название рецепта',
        blank=False,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='images/',
        blank=False,
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        blank=False,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        blank=False,
        validators=[MinValueValidator(
            1,
            'Время приготовления не может быть меньше 1 минуты',
        )],
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name='recipes_ingredient',
        through='IngredientAmount',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
    )
    pub_date = models.DateTimeField(
        verbose_name='Время публикации',
        auto_now_add=True,
    )
    objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} - {self.author.username}'


class IngredientAmount(models.Model):
    """Модель количества ингредиентов в рецепте,
       связаная через модели рецептов и ингредиентов"""
    ingredient = models.ForeignKey(
        Ingredients,
        max_length=MAX_CHAR_LENGTH_254,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='amount_ingredients',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(
            1,
            'Количество не может быть меньше 1'
        )],
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='amount_ingredients',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_combination'
            ),
        )
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = 'Количества ингредиента в рецепте'

    def __str__(self):
        return (
            f'{self.recipe.name} - {self.ingredient.name} '
            f'{self.amount}{self.ingredient.measurement_unit} '
            f'{self.ingredient.name}'
        )


class Favorites(models.Model):
    """Модель избранных рецепотв"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(models.Model):
    """Модель корзины """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
