import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Import data from CSV file into Django models'
    csv_path = (
        Path(__file__).resolve().parent.parent.parent.parent / 'data'
    )
    file_names = ('ingredients.csv', 'tags.csv')

    def handle(self, *args, **options):
        # Имортируем данные из csv-файлов в соответствующие модели
        for file in self.file_names:
            csv_file_path = self.csv_path / file
            with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    if file == 'ingredients.csv':
                        instance = Ingredient(
                            name=row[0],
                            measurement_unit=row[1]
                        )
                        instance.save()

                    elif file == 'tags.csv':
                        instance = Tag(
                            name=row[0],
                            color=row[1],
                            slug=row[2]
                        )
                        instance.save()

            self.stdout.write(
                self.style.SUCCESS(f'{file} imported successfully!')
            )
