from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db import IntegrityError


class Command(BaseCommand):
    help = "Создает суперпользователя, если он не создан"

    def handle(self, *args, **options):
        user = get_user_model()
        try:
            if not user.objects.filter(email="admin@sky.pro").exists():
                user.objects.create_superuser(
                    email="admin@sky.pro",
                    password="123qwe456rty",
                    first_name="Admin",
                    last_name="Admin",
                    username="Admin",
                )
                self.stdout.write(self.style.SUCCESS("Суперпользователь admin@sky.pro успешно создан"))
            else:
                self.stdout.write(self.style.WARNING("Суперпользователь admin@sky.pro уже существует"))
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f"Ошибка создания суперпользователя: {e}"))
