from celery import shared_task
from django.core.mail import send_mail

from config import settings


@shared_task
def send_activation_email(email, activation_link):
    """Асинхронная отправка письма активации"""

    full_link = f"{settings.FRONTEND_URL}{activation_link}"

    send_mail(
        subject="Подтверждение регистрации",
        message=f"Перейдите по ссылке для активации: {full_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )
