# accounts/management/commands/send_newsletter.py
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mass_mail, send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Отправляет новостную рассылку всем подтвержденным пользователям'

    def add_arguments(self, parser):
        """
        Добавляет аргументы командной строки
        """
        parser.add_argument(
            '--subject',
            type=str,
            required=True,
            help='Тема письма'
        )

        parser.add_argument(
            '--message',
            type=str,
            required=True,
            help='Текст письма (можно использовать файл: @filename.txt)'
        )

        parser.add_argument(
            '--file',
            type=str,
            help='Файл с текстом письма'
        )

        parser.add_argument(
            '--recipients',
            type=str,
            choices=['all', 'active', 'verified', 'test'],
            default='verified',
            help='Кому отправлять: all - всем, active - активным, verified - подтвержденным (по умолчанию), test - только тестовым'
        )

        parser.add_argument(
            '--test-emails',
            type=str,
            help='Список тестовых email через запятую для recipients=test'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Режим проверки: показать получателей, но не отправлять письма'
        )

        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Количество писем в одной партии (для избежания перегрузки)'
        )

    def handle(self, *args, **options):
        """
        Основная логика команды
        """
        subject = options['subject']
        message = options['message']
        recipients_type = options['recipients']
        dry_run = options['dry_run']
        batch_size = options['batch_size']

        # Загружаем сообщение из файла, если указано
        if options.get('file'):
            try:
                with open(options['file'], 'r', encoding='utf-8') as f:
                    message = f.read()
                self.stdout.write(self.style.SUCCESS(f'Сообщение загружено из файла: {options["file"]}'))
            except FileNotFoundError:
                raise CommandError(f'Файл {options["file"]} не найден')

        # Получаем список получателей
        recipients = self.get_recipients(recipients_type, options.get('test_emails'))

        if not recipients:
            self.stdout.write(self.style.WARNING('Нет получателей для рассылки'))
            return

        self.stdout.write(self.style.SUCCESS(f'Найдено получателей: {len(recipients)}'))

        if dry_run:
            self.stdout.write(self.style.WARNING('РЕЖИМ DRY-RUN: письма НЕ будут отправлены'))
            self.print_recipients(recipients)
            return

        # Отправляем рассылку
        self.send_newsletter(subject, message, recipients, batch_size)

    def get_recipients(self, recipients_type, test_emails=None):
        """
        Получает список email получателей в зависимости от типа
        """
        if recipients_type == 'all':
            users = User.objects.all()
        elif recipients_type == 'active':
            users = User.objects.filter(is_active=True)
        elif recipients_type == 'verified':
            users = User.objects.filter(is_verified=True, is_active=True)
        elif recipients_type == 'test':
            if not test_emails:
                raise CommandError('Для recipients=test необходимо указать --test-emails')
            # Разбираем список email через запятую
            emails = [email.strip() for email in test_emails.split(',')]
            return emails
        else:
            users = User.objects.filter(is_verified=True, is_active=True)

        # Извлекаем email из пользователей
        return [user.email for user in users if user.email]

    def print_recipients(self, recipients):
        """
        Выводит список получателей в консоль
        """
        self.stdout.write(self.style.WARNING('Список получателей:'))
        for i, email in enumerate(recipients[:20], 1):  # Показываем первые 20
            self.stdout.write(f'  {i}. {email}')

        if len(recipients) > 20:
            self.stdout.write(f'  ... и еще {len(recipients) - 20} получателей')

    def send_newsletter(self, subject, message, recipients, batch_size):
        """
        Отправляет рассылку партиями
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        total = len(recipients)
        sent = 0
        failed = 0

        self.stdout.write(self.style.SUCCESS(f'Начинаю отправку рассылки "{subject}"'))
        self.stdout.write(f'Всего получателей: {total}')

        # Отправляем партиями
        for i in range(0, total, batch_size):
            batch = recipients[i:i + batch_size]

            # Создаем кортежи для массовой отправки
            messages = []
            for email in batch:
                messages.append((
                    subject,
                    message,
                    from_email,
                    [email]
                ))

            try:
                # send_mass_mail возвращает количество успешно отправленных писем
                result = send_mass_mail(messages, fail_silently=False)
                sent += result

                self.stdout.write(f'  Отправлено: {i + len(batch)}/{total}', ending='\r')

            except Exception as e:
                failed += len(batch)
                logger.error(f'Ошибка при отправке партии: {e}')
                self.stdout.write(self.style.ERROR(f'\nОшибка в партии: {e}'))

        # Итоговый отчет
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'Рассылка завершена!'))
        self.stdout.write(f'Успешно отправлено: {sent}')
        self.stdout.write(f'Ошибок: {failed}')
        self.stdout.write('=' * 50)
