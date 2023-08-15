import csv
from pathlib import Path
from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag

User = get_user_model()


class Command(BaseCommand):
    help = 'Import data from CSV file into Django models'
    csv_path = (
        Path(__file__).resolve().parent.parent.parent.parent.parent.parent
        / 'data'
    )
    file_names = ('ingredients.csv', 'tags.csv', 'users.csv')

    def handle(self, *args, **options):
        # Создаем суперюзера 'admin' (если еще не создан):
        username = 'admin'
        password = '412656'
        email = 'admin@admin.com'
        first_name = 'admin'
        last_name = 'admin'
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            self.stdout.write(
                self.style.SUCCESS('Superuser created successfully!')
            )

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

                    elif file == 'users.csv':
                        instance = User(
                            email=row[0],
                            username=row[1],
                            first_name=row[2],
                            last_name=row[3],
                            password=row[4],
                        )
                        instance.save()

            self.stdout.write(
                self.style.SUCCESS(f'{file} imported successfully!')
            )
