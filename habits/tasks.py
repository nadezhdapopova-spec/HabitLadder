from collections import defaultdict
from datetime import date
from celery import shared_task
from django.utils import timezone
from habits.models import Habit
from habits.services import send_telegram_message


@shared_task
def send_habit_reminder():
    """Отправляет пользователю напоминание о ближайшей привычке через телеграм-бота"""
    now = timezone.localtime()
    now_time = now.time().replace(second=0, microsecond=0)

    habits = Habit.objects.filter(habit_time=now_time)

    for habit in habits:
        days_passed = (date.today() - habit.created_at.date()).days
        if days_passed % habit.periodicity == 0:
            message = f"Время выполнить привычку: {habit.action}. Это займет всего 2 минуты — ты справишься!"
            send_telegram_message(habit.user.tg_chat_id, message)
