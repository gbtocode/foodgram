# Generated by Django 3.2.3 on 2024-05-27 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_ingredients_unique_name_measurement_unit'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ingredientamount',
            name='unique_ingredient_in_recipe',
        ),
        migrations.RemoveConstraint(
            model_name='ingredients',
            name='unique_name_measurement_unit',
        ),
        migrations.AddConstraint(
            model_name='ingredientamount',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_combination'),
        ),
    ]
