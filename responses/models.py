# responses/models.py
from django.db import models
from django.conf import settings
from posts.models import Post


class Response(models.Model):
    """Response to a post"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='responses')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='responses')
    text = models.TextField('Текст отклика', max_length=1000)
    is_accepted = models.BooleanField('Принят', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return f'Отклик от {self.author.username} на "{self.post.title}"'

    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'
        ordering = ['-created_at']
