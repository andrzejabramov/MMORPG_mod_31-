# responses/admin.py
from django.contrib import admin
from .models import Response

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('text', 'author__email', 'post__title')
    raw_id_fields = ('post', 'author')
    date_hierarchy = 'created_at'
