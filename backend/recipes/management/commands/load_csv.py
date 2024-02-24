import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient
# import subprocess

models_1 = [
    (Ingredient, 'ingredients.csv')
]

# Если нужны связи
# models_2 = [
#     ('recipes_ingredients', 'ingredients.csv')
# ]


class Command(BaseCommand):
    help_text = 'load ingredient models'

    def handle(self, *args, **options):
        log_file = open('load_csv.log', 'w', encoding='UTF-8')
        path = 'static/data/'
        records = {}
        for model, file_name in models_1:
            with open(f'{path}{file_name}', 'r', encoding='UTF-8') as file:
                rows = csv.DictReader(file)
                records[model.__name__] = [model.objects.create(**row) for row in rows]
            self.stdout.write(self.style.SUCCESS(f'Done {file_name}'))
        # for model, file_name in models_2:
        #     s = subprocess.call([
        #         'sqlite3', 'db.sqlite3', '.mode csv',
        #         f'.import {path}{file_name} {model}'
        #     ], stderr=log_file)
        #     self.stdout.write(self.style.SUCCESS(f'Done {file_name}'))
