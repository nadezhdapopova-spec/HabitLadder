from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone
from datetime import time, timedelta
from zoneinfo import ZoneInfo

from habits.models import Habit
from users.models import CustomUser
from habits.tasks import send_habit_reminder


class HabitReminderTests(TestCase):
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
            action="Drink water",
            place="home",
            habit_time=time(10, 0),
            periodicity=1,
            reward="test reward",
        )

    @patch("habits.tasks.send_telegram_message.delay")
    def test_reminder_sent_at_correct_time(self, mock_delay):
        """Проверяет, что сообщение отправляется в нужный момент"""
        # Время сейчас — 10:00 по Москве
        fake_now = timezone.datetime(2024, 1, 1, 7, 0, tzinfo=timezone.utc)

        with patch("django.utils.timezone.now", return_value=fake_now):
            send_habit_reminder()

        mock_delay.assert_called_once()

    @patch("habits.tasks.send_telegram_message.delay")
    def test_no_message_if_time_does_not_match(self, mock_delay):
        """Если время не совпало, ничего не отправляется"""
        # 10:01 по Москве (разница в минуту)
        fake_now = timezone.datetime(2024, 1, 1, 7, 1, tzinfo=timezone.utc)

        with patch("django.utils.timezone.now", return_value=fake_now):
            send_habit_reminder()

        mock_delay.assert_not_called()

    @patch("habits.tasks.send_telegram_message.delay")
    def test_periodicity_respected(self, mock_delay):
        """Проверяет, что периодичность отправки считается корректно"""
        # привычка создана 3 дня назад
        self.habit.created_at = timezone.now() - timedelta(days=3)
        self.habit.periodicity = 3
        self.habit.save()

        fake_now = timezone.now().astimezone(ZoneInfo("Europe/Moscow"))
        fake_now = fake_now.replace(hour=10, minute=0)

        with patch("django.utils.timezone.now", return_value=fake_now):
            send_habit_reminder()

        mock_delay.assert_called_once()

    @patch("habits.tasks.send_telegram_message.delay")
    def test_message_text_is_correct(self, mock_delay):
        """Проверяется, что отправляется корректный текст"""
        fake_now = timezone.datetime(2024, 1, 1, 7, 0, tzinfo=timezone.utc)

        with patch("django.utils.timezone.now", return_value=fake_now):
            send_habit_reminder()

        args, kwargs = mock_delay.call_args
        chat_id, message = args

        self.assertIn("Drink water", message)
        self.assertIn("награду: test reward", message)
