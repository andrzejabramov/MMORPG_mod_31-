# posts/admin.py
from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Category, Post

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_name_display')
    list_filter = ('name',)

@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content', 'author__email')
    summernote_fields = ('content',)
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'
