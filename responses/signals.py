# responses/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Response


@receiver(post_save, sender=Response)
def notify_author_on_new_response(sender, instance, created, **kwargs):
    """
    Сигнал: при создании нового отклика отправляем уведомление автору объявления
    """
    if created:
        post = instance.post
        post_author = post.author
        response_author = instance.author

        # Не отправляем уведомление, если автор отвечает на свое объявление
        if post_author == response_author:
            return

        subject = f'Новый отклик на ваше объявление: {post.title}'
        message = f"""
Здравствуйте, {post_author.username}!

На ваше объявление "{post.title}" оставил отклик пользователь {response_author.username}.

Текст отклика:
{instance.text}

---
Вы можете принять или отклонить этот отклик на странице управления откликами:
{settings.SITE_URL}/responses/

С уважением,
Администрация MMORPG Fan Board
        """

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [post_author.email]

        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            # Логирование ошибки, но без print
            pass


@receiver(post_save, sender=Response)
def notify_author_on_response_accepted(sender, instance, created, **kwargs):
    """
    Сигнал: при принятии отклика отправляем уведомление автору отклика
    """
    # Проверяем, что это не создание, а обновление, и is_accepted стало True
    if not created and instance.is_accepted:
        # Проверяем, было ли это изменение (чтобы не отправлять при каждом сохранении)
        try:
            # Получаем предыдущее состояние из базы данных
            old_instance = Response.objects.get(pk=instance.pk)
            if old_instance.is_accepted == instance.is_accepted:
                return  # Статус не изменился
        except Response.DoesNotExist:
            return

        post = instance.post
        response_author = instance.author

        subject = 'Ваш отклик принят!'
        message = f"""
Здравствуйте, {response_author.username}!

Ваш отклик на объявление "{post.title}" был принят автором.

Текст вашего отклика:
{instance.text}

---
Вы можете посмотреть объявление по ссылке:
{settings.SITE_URL}{post.get_absolute_url()}

С уважением,
Администрация MMORPG Fan Board
        """

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [response_author.email]

        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            # Логирование ошибки, но без print
            pass