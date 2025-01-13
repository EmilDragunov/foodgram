import json
import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из JSON или CSV файла.'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str,
                            help='Путь к файлу с ингредиентами')
        parser.add_argument('--filetype', type=str,
                            choices=['json', 'csv'],
                            default='json', help='Тип файла: json или csv')

    def handle(self, *args, **options):
        file_path = options['file_path']
        filetype = options['filetype']

        try:
            if filetype == 'json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for item in data:
                    Ingredient.objects.create(name=item['name'],
                                              measurement_unit=item[
                                                  'measurement_unit'])

            elif filetype == 'csv':
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        Ingredient.objects.create(name=row['name'],
                                                  measurement_unit=row[
                                                      'measurement_unit'])

            self.stdout.write(self.style.SUCCESS(
                'Ингредиенты успешно импортированы.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка импорта: {e}'))
