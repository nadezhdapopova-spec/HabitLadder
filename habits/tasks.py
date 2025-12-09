from datetime import date
from celery import shared_task
from django.utils import timezone
from habits.models import Habit
import requests
from config.settings import TELEGRAM_URL, TELEGRAM_TOKEN


@shared_task
def send_telegram_message(chat_id, message):
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
    """Формирует напоминание о привычке пользователю и отправляет в Телеграм"""
    now = timezone.now()
    now_hour_minute = now.replace(second=0, microsecond=0).time()

    habits = Habit.objects.filter(
        habit_time__hour=now_hour_minute.hour,
        habit_time__minute=now_hour_minute.minute,
        user__tg_chat_id__isnull=False,
    ).select_related("user")

    # print("NOW:", timezone.localtime())
    # print("NOW TIME:", now_hour_minute)
    # print("ALL HABITS:", Habit.objects.all().values("id", "habit_time"))
    # print("HABITS TO SEND:", list(habits.values("id", "habit_time", "user__tg_chat_id")))
    #
    # print(habits)
    for habit in habits:
        date_passed = (date.today() - habit.created_at.date()).days
        if habit.created_at.date() == date.today() or date_passed % habit.periodicity == 0:
            message = f"Время выполнить привычку: {habit.action}. Это займет всего 2 минуты — ты справишься!"
            send_telegram_message.delay(habit.user.tg_chat_id, message)
