# Generated by Django 3.2.3 on 2024-02-02 07:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_rename_quantity_ingredient_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='user',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='cook_time',
            new_name='cooking_time',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='title',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='description',
            new_name='text',
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='color_code',
            new_name='color',
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='title',
            new_name='name',
        ),
    ]