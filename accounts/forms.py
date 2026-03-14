# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Обязательное поле')

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')


class VerifyForm(forms.Form):
    code = forms.CharField(max_length=6, label='Код подтверждения')
