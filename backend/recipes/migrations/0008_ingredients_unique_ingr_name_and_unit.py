# Generated by Django 3.2.3 on 2024-05-30 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20240527_1636'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='ingredients',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_ingr_name_and_unit'),
        ),
    ]
