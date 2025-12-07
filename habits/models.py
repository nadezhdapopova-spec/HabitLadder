from django.db import models


class Habit(models.Model):
    """Модель позитивной привычки"""

    user = models.ForeignKey(
        to="users.CustomUser",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="habits")
    action = models.CharField(
        max_length=500,
        verbose_name="Действие",
        help_text="Напишите, что планируете сделать (например, поприседать 20 раз)")
    place = models.CharField(
        max_length=500,
        verbose_name="Место выполнения привычки",
        help_text="Укажите, где: например, дома, в парке и др.")
    habit_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Время начала выполнения привычки")
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Частота выполнения привычки в днях",
        help_text="Например, 1 → каждый день, 2 → раз в два дня (не более семи дней)")
    duration = models.PositiveSmallIntegerField(
        default=120,
        verbose_name="Количество времени для выполнения (в секундах)",
        help_text="Не более 120 секунд")
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки",
        help_text="Является ли привычка приятной")
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_to",
        verbose_name="Связанная приятная привычка",
        help_text="Приятная привычка, выполняемая как вознаграждение (если не указано вознаграждение)")
    reward = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="Вознаграждение",
        help_text="Вознаграждение (если нет связанной приятной привычки)")
    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичная привычка",
        help_text="Сделать привычку видимой для других пользователей")
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания")
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата последнего изменения")

    def __str__(self):
        """Строковое отображение урока"""
        return f"Я буду {self.action} в {self.habit_time} в {self.place}"

    class Meta:
        unique_together = ("user", "action", "place")
        verbose_name = "привычка"
        verbose_name_plural = "привычки"
        ordering = ["periodicity", "habit_time"]
