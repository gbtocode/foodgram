import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredients, Tag


class Command(BaseCommand):
    help = ' Загрузить данные в модель ингредиентов '

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Старт команды'))
        with open('data/ingredients.json', encoding='utf-8',
                  ) as data_file_ingredients:
            ingredient_data = json.loads(data_file_ingredients.read())
            for ingredient in ingredient_data:
                if not Ingredients.objects.filter(
                        name=ingredient['name']).exists():
                    Ingredients.objects.create(**ingredient)

        with open('data/tags.json', encoding='utf-8',
                  ) as data_file_tags:
            tags_data = json.loads(data_file_tags.read())
            for tags in tags_data:
                Tag.objects.create(**tags)

        self.stdout.write(self.style.SUCCESS('Данные загружены'))
