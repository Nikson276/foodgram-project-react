# Generated by Django 3.2.3 on 2024-02-02 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20240202_1018'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Follow',
        ),
    ]