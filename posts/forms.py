# posts/forms.py
from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category']
        widgets = {
            'content': SummernoteWidget(),
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Содержание',
            'category': 'Категория',
        }
