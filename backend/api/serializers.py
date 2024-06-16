from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorites, IngredientAmount, Ingredients, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from users.models import Subscriber, User
from users.serializers import UsersSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class IngredientAmountCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиента и его количества"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1,)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount',)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта"""
    tags = TagSerializer(many=True)
    author = UsersSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True,
        source='amount_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags',
            'author', 'ingredients',
            'image', 'is_favorited',
            'is_in_shopping_cart', 'cooking_time',
            'name', 'text',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return False if user.is_anonymous else Favorites.objects.filter(
            recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return False if user.is_anonymous else ShoppingCart.objects.filter(
            recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientAmountCreateSerializer(many=True)
    image = Base64ImageField(required=True)
    author = UsersSerializer(read_only=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags',
            'image', 'author',
            'cooking_time', 'name',
            'text', 'ingredients',
        )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Нужен минимум 1 ингредиент')
        ingredients_list = []
        for item in value:
            try:
                ingredient = Ingredients.objects.get(id=item['id'])
            except Ingredients.DoesNotExist:
                raise serializers.ValidationError(
                    'Такого ингредиента не существует'
                )
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты не могут повторяться!'
                )
            if int(item['amount']) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента не дожно быть меньше нуля'
                )
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError('Нужен минимум 1 тег')
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Теги должны быть уникальными')
        return value

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше нуля'
            )
        return value

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Изображение обязательно к заполнению!'
            )
        return value

    def create_ingredients(self, ingredients, recipe):
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_instance = Ingredients.objects.get(id=ingredient['id'])
            ingredient_list.append(
                IngredientAmount(
                    amount=ingredient['amount'],
                    ingredient=ingredient_instance,
                    recipe=recipe,
                )
            )
        IngredientAmount.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients=ingredients_data, recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' not in validated_data:
            raise serializers.ValidationError(
                'Ингредиенты обязательны к заполнению!'
            )
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)
        if 'tags' not in validated_data:
            raise serializers.ValidationError(
                'Теги обязательны к заполнению!'
            )
        instance.tags.set(validated_data.pop('tags'))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance,
                                    context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор коризны покупок"""
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)


class MiniRecipeSerializer(RecipeReadSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriberSerializer(serializers.ModelSerializer):
    """Сериализатор управления подписками"""
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    username = serializers.ReadOnlyField(source='author.username')
    email = serializers.ReadOnlyField(source='author.email')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    author = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscriber
        fields = (
            'id', 'first_name',
            'last_name', 'username',
            'email', 'recipes',
            'recipes_count', 'is_subscribed',
            'author',
        )

    def validate(self, data):
        user = self.context['request'].user
        author_to_sub = data['author']

        if user == author_to_sub:
            raise ValidationError('Нельзя подписаться на самого себя!')
        if Subscriber.objects.filter(
            author=user,
            subscriber=author_to_sub
        ).exists():
            raise ValidationError('Вы уже подписались на этого пользователя!')
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        author_to_sub = validated_data['author']
        subs, created = Subscriber.objects.get_or_create(
            author=user,
            subscriber=author_to_sub
        )
        if not created:
            raise ValidationError('Подписка уже существует')
        return subs

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscriber.objects.filter(
            author=obj.author,
            subscriber=user
        ).exists()

    def get_recipes(self, obj):
        if 'recipes_limit' in self.context['request'].query_params:
            recipes_limit = int(self.context['request'].
                                query_params['recipes_limit'])
            queryset = obj.author.recipes.all()[:recipes_limit]
            return MiniRecipeSerializer(queryset, many=True).data
        queryset = obj.author.recipes.all()
        return MiniRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.all().count()


class SubscriptionSerializer(UsersSerializer):
    """Сериализатор для эндпоинта subscription"""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email',
            'username', 'first_name',
            'last_name', 'is_subscribed',
            'recipes', 'recipes_count',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscriber.objects.filter(
            subscriber=user,
            author=obj.id).exists()

    def get_recipes(self, obj):
        if 'recipes_limit' in self.context['request'].query_params:
            recipes_limit = int(self.context['request'].
                                query_params['recipes_limit'])
            queryset = obj.recipes.all()[:recipes_limit]
            return MiniRecipeSerializer(queryset, many=True).data
        queryset = obj.recipes.all()
        return MiniRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов"""
    class Meta:
        model = Favorites
        fields = ('user', 'recipe',)
