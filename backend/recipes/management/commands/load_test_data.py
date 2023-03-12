import json

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag
from users.models import CustomUser

TABLES = {
    Ingredient: 'ingredients.json',
    Tag: 'tags.json',
    CustomUser: 'users.json',
}


class Command(BaseCommand):
    help = ' Загрузка тестовых данных. '

    def handle(self, *args, **options):
        for model, json_file in TABLES.items():
            self.stdout.write(f'Импорт данных из файла {json_file}')
            with open(f'{settings.BASE_DIR}/data/{json_file}',
                      encoding='utf-8',) as file:
                counter = 0
                test_data = json.loads(file.read())
                for element in test_data:
                    model.objects.get_or_create(**element)
                    counter += 1
            self.stdout.write(self.style.SUCCESS(
                        f'- загружено {counter} записей'))
