from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Subscriber, User


class UsersSerializer(UserSerializer):
    """Сериализатор пользователя"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email',
            'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscriber.objects.filter(
            subscriber=user,
            author=obj.id).exists()


class UsersCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя"""
    username = serializers.CharField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Пользователь с таким логином уже существует'
        )]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Пользователь с таким email уже существует'
        )]
    )

    class Meta:
        model = User
        fields = (
            'id', 'email',
            'username', 'password',
            'first_name', 'last_name',
        )
