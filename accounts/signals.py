## accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import logging
from .models import OneTimeCode, User

logger = logging.getLogger(__name__)

@receiver(post_save, sender=OneTimeCode)
def send_verification_code(sender, instance, created, **kwargs):
    """
    Сигнал: при создании кода подтверждения отправляем его на email
    """
    if created:
        user = instance.user
        code = instance.code

        # Проверяем, что у пользователя есть email
        if not user.email:
            logger.error(f"Попытка отправить код пользователю без email: {user.username}")
            return

        subject = 'Код подтверждения регистрации на MMORPG Fan Board'
        message = f"""
Здравствуйте, {user.username}!

Для завершения регистрации на сайте MMORPG Fan Board введите следующий код подтверждения:

🔐 Код: {code}

Код действителен в течение 24 часов.

Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.

Ссылка для подтверждения: {settings.SITE_URL}/accounts/verify/

С уважением,
Администрация MMORPG Fan Board
        """

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        try:
            sent_count = send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )
            if sent_count == 1:
                logger.info(f"Код подтверждения успешно отправлен на {user.email}")
                print(f"✅ Код подтверждения отправлен на {user.email}")
            else:
                logger.warning(f"Письмо не было отправлено на {user.email}")
        except Exception as e:
            logger.error(f"Ошибка при отправке кода на {user.email}: {e}")
            print(f"❌ Ошибка отправки письма: {e}")
            # Здесь можно добавить логику для повторной отправки или уведомления