# responses/apps.py
from django.apps import AppConfig


class ResponsesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'responses'
    verbose_name = 'Отклики'

    def ready(self):
        import responses.signals  # noqa
