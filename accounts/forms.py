# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Обязательное поле')

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and len(username) < 3:
            raise forms.ValidationError('Имя пользователя должно содержать минимум 3 символа.')
        return username


class VerifyForm(forms.Form):
    code = forms.CharField(max_length=6, label='Код подтверждения')