# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import OneTimeCode, User


@receiver(post_save, sender=OneTimeCode)
def send_verification_code(sender, instance, created, **kwargs):
    """
    Сигнал: при создании кода подтверждения отправляем его на email
    """
    if created:
        user = instance.user
        code = instance.code

        subject = 'Код подтверждения регистрации'
        message = f"""
Здравствуйте!

Для завершения регистрации на сайте MMORPG Fan Board введите следующий код подтверждения:

Код: {code}

Код действителен в течение 24 часов.

Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.

С уважением,
Администрация MMORPG Fan Board
        """

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            print(f"Код подтверждения отправлен на {user.email}")  # для отладки
        except Exception as e:
            print(f"Ошибка при отправке кода: {e}")
