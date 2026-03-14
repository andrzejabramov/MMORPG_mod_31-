# responses/forms.py
from django import forms
from .models import Response

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text']
        labels = {
            'text': 'Ваш отклик',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Напишите ваш отклик...'}),
        }
