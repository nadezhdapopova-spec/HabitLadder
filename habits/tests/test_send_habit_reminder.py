from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone, time, timedelta
from zoneinfo import ZoneInfo

from habits.models import Habit
from users.models import CustomUser
from habits.tasks import send_habit_reminder


class HabitReminderTests(TestCase):
    """Тестирует отправку пользователю напоминание о привычке с учетом его часового пояса"""
    def setUp(self):
        """Формирует тестовые данные"""
        self.user = CustomUser.objects.create_user(
            email="user@test.com",
            username="user",
            password="pass123",
            tg_chat_id="111",
            timezone="Europe/Moscow"
        )

        self.habit = Habit.objects.create(
            user=self.user,
            action="Выпить стакан воды",
            place="дома",
            habit_time=time(10, 0),
            periodicity=1,
            reward="съесть конфету",
        )

    @patch("habits.tasks.send_telegram_message.delay")
    def test_reminder_sent_at_correct_time(self, mock_delay):
        """Проверяет, что сообщение отправляется в нужный момент"""
        fake_now = datetime(2024, 1, 1, 7, 0, tzinfo=dt_timezone.utc)

        with patch("django.utils.timezone.now", return_value=fake_now):
            send_habit_reminder()

        mock_delay.assert_called_once()

    @patch("habits.tasks.send_telegram_message.delay")
    def test_if_time_does_not_match(self, mock_delay):
        """Если время не совпало, ничего не отправляется"""
        fake_now = datetime(2024, 1, 1, 7, 1, tzinfo=dt_timezone.utc)

        with patch("django.utils.timezone.now", return_value=fake_now):
            send_habit_reminder()

        mock_delay.assert_not_called()

    @patch("habits.tasks.send_telegram_message.delay")
    def test_periodicity_respected(self, mock_delay):
        """Проверяет, что периодичность отправки считается корректно"""
        now_utc = datetime(2024, 1, 4, 7, 0, tzinfo=dt_timezone.utc)  # пример "сейчас" в UTC
        created_utc = now_utc - timedelta(days=3)

        self.habit.created_at = created_utc
        self.habit.periodicity = 3
        self.habit.save()

        fake_now_utc = now_utc
        with patch("django.utils.timezone.now", return_value=fake_now_utc):
            send_habit_reminder()

        mock_delay.assert_called_once()
