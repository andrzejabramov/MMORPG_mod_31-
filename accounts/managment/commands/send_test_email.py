# accounts/management/commands/send_test_email.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Отправляет тестовое письмо для проверки настроек почты'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email для отправки тестового письма'
        )

        parser.add_argument(
            '--to-admin',
            action='store_true',
            help='Отправить тестовое письмо администратору (первому суперпользователю)'
        )

    def handle(self, *args, **options):
        """
        Отправляет тестовое письмо
        """
        email = options.get('email')
        to_admin = options.get('to_admin')

        # Определяем получателя
        recipient = None

        if email:
            recipient = email
            self.stdout.write(f'Отправка тестового письма на: {recipient}')

        elif to_admin:
            admin = User.objects.filter(is_superuser=True).first()
            if admin:
                recipient = admin.email
                self.stdout.write(f'Отправка тестового письма администратору: {recipient}')
            else:
                self.stdout.write(self.style.ERROR('Администратор не найден'))
                return

        else:
            # Если не указан получатель, используем первый email из настроек
            recipient = settings.DEFAULT_FROM_EMAIL
            self.stdout.write(f'Отправка тестового письма на: {recipient} (DEFAULT_FROM_EMAIL)')

        # Тема и текст письма
        subject = 'Тестовое письмо от MMORPG Fan Board'
        message = f"""
Здравствуйте!

Это тестовое письмо отправлено с помощью команды send_test_email.

Время отправки: {self.get_current_time()}
Настройки почты:
- EMAIL_HOST: {settings.EMAIL_HOST}
- EMAIL_PORT: {settings.EMAIL_PORT}
- EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}
- DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}

Если вы получили это письмо, значит почтовые настройки работают правильно!

С уважением,
Администрация MMORPG Fan Board
        """

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('✅ Тестовое письмо успешно отправлено!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка при отправке: {e}'))

    def get_current_time(self):
        """Возвращает текущее время в читаемом формате"""
        from django.utils import timezone
        return timezone.now().strftime('%d.%m.%Y %H:%M:%S')
