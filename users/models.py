from django.contrib.auth.models import AbstractUser
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField


class City(models.Model):
    """Класс модели города (РФ)"""

    name = models.CharField(max_length=100, unique=True, verbose_name="Город")

    def __str__(self):
        """Строковое отображение города"""
        return self.name


class CustomUser(AbstractUser):
    """Класс модели пользователя"""

    TIMEZONES = [
        ("Europe/Moscow", "Москва"),
        ("Europe/Kaliningrad", "Калининград"),
        ("Asia/Yekaterinburg", "Екатеринбург"),
        ("Asia/Novosibirsk", "Новосибирск"),
        ("Asia/Krasnoyarsk", "Красноярск"),
        ("Asia/Irkutsk", "Иркутск"),
        ("Asia/Yakutsk", "Якутск"),
        ("Asia/Vladivostok", "Владивосток"),
        ("Asia/Sakhalin", "Сахалин"),
        ("Asia/Magadan", "Магадан"),
        ("Asia/Kamchatka", "Камчатка"),
    ]

    email = models.EmailField(unique=True, verbose_name="Email")
    phone_number = PhoneNumberField(
        region="RU", blank=True, null=True, verbose_name="Номер телефона", help_text="Необязательное поле"
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
        default="default/default.png",
        help_text="Необязательное поле",
    )
    city = models.ForeignKey(to=City, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Город")
    timezone = models.CharField(max_length=32, choices=TIMEZONES, default="Europe/Moscow")
    tg_chat_id = models.BigIntegerField(
        blank=True, null=True, verbose_name="Telegram chat-id", help_text="Укажите свой телеграм chat-id"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    def __str__(self):
        """Строковое отображение пользователя"""
        return self.username or self.email

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        ordering = [
            "email",
        ]
