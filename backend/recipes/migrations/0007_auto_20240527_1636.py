# Generated by Django 3.2.3 on 2024-05-27 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20240527_1629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredients',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Название ингредиента'),
        ),
        migrations.AddConstraint(
            model_name='ingredientamount',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_combination'),
        ),
    ]
