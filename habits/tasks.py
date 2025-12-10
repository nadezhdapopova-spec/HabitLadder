from zoneinfo import ZoneInfo

from django.utils import timezone

import requests
from celery import shared_task

from config.settings import TELEGRAM_TOKEN, TELEGRAM_URL
from habits.models import Habit


@shared_task
def send_telegram_message(chat_id: int, message: str):
    """Отправляет сообщение в Телеграм"""
    params = {
        "text": message,
        "chat_id": chat_id,
    }
    url = f"{TELEGRAM_URL}{TELEGRAM_TOKEN}/sendMessage"
    response = requests.post(url, params=params)
    if response.status_code != 200:
        print("Telegram error:", response.text)


@shared_task
def send_habit_reminder():
    """Отправляет пользователю напоминание о привычке с учетом его часового пояса"""
    now_utc = timezone.now()
    habits = Habit.objects.filter(user__tg_chat_id__isnull=False).select_related("user")

    for habit in habits:
        user_tz = ZoneInfo(habit.user.timezone)
        user_now = now_utc.astimezone(user_tz)
        if (user_now.hour, user_now.minute) != (habit.habit_time.hour, habit.habit_time.minute):
            continue

        created_local = habit.created_at.astimezone(user_tz).date()
        days_passed = (user_now.date() - created_local).days
        if habit.created_at.date() == user_now.date() or days_passed % habit.periodicity == 0:
            message = f"Время выполнить привычку: {habit.action}. Это займет всего 2 минуты — ты справишься!"
            if habit.reward:
                message += f" После выполнения ты получишь награду: {habit.reward}"
            if habit.related_habit:
                message += f" А ещё тебя ждёт приятная привычка: {habit.related_habit.action}"
            send_telegram_message.delay(habit.user.tg_chat_id, message)
