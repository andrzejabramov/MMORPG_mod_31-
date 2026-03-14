# posts/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse


class Category(models.Model):
    """Post category model with fixed choices"""
    TANKS = 'TK'
    HEALS = 'HL'
    DD = 'DD'
    MERCHANTS = 'MR'
    GUILD_MASTERS = 'GM'
    QUEST_GIVERS = 'QG'
    BLACKSMITHS = 'BS'
    LEATHERWORKERS = 'LW'
    POTION_MAKERS = 'PM'
    SPELL_MASTERS = 'SM'

    CATEGORY_CHOICES = [
        (TANKS, 'Танки'),
        (HEALS, 'Хилы'),
        (DD, 'ДД'),
        (MERCHANTS, 'Торговцы'),
        (GUILD_MASTERS, 'Гилдмастеры'),
        (QUEST_GIVERS, 'Квестгиверы'),
        (BLACKSMITHS, 'Кузнецы'),
        (LEATHERWORKERS, 'Кожевники'),
        (POTION_MAKERS, 'Зельевары'),
        (SPELL_MASTERS, 'Мастера заклинаний'),
    ]

    name = models.CharField(max_length=2, choices=CATEGORY_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Post(models.Model):
    """Bulletin board post"""
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='posts')
    title = models.CharField('Заголовок', max_length=255)
    content = models.TextField('Содержание')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']
