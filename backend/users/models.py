from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint
from recipes.constants import MAX_CHAR_LENGTH_150, MAX_CHAR_LENGTH_254


class User(AbstractUser):
    """Переопределенная модель пользователя"""
    username = models.CharField(
        'Юзернейм',
        max_length=MAX_CHAR_LENGTH_150,
        unique=True,
    )
    email = models.EmailField(
        'Адрес почты',
        max_length=MAX_CHAR_LENGTH_254,
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_CHAR_LENGTH_150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_CHAR_LENGTH_150,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscriber(models.Model):
    """Модель подписок"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipe_author'
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscriber'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(
                fields=('author', 'subscriber',),
                name='Unique subscribe',
            ),
        ]

        def __str__(self):
            return (f'{self.subscriber} '
                    f'подписался на {self.author}')
