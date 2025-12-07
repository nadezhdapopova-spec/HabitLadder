from django.core.management import call_command
from django.core.management.base import BaseCommand

from users.models import City, CustomUser


class Command(BaseCommand):
    help = "Добавляет тестовые данные пользователей в БД из фикстур"

    def handle(self, *args, **kwargs):
        City.objects.all().delete()
        CustomUser.objects.all().delete()

        call_command("loaddata", "users/fixtures/cities_fixture.json")
        self.stdout.write(self.style.SUCCESS("Загружены города из фикструры"))

        call_command("loaddata", "users/fixtures/users_fixture.json")
        self.stdout.write(self.style.SUCCESS("Загружены пользователи из фикструры"))

        self.stdout.write(self.style.SUCCESS("Данные успешно загружены"))
