# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .forms import SignUpForm, VerifyForm
from .models import OneTimeCode, User


def signup(request):
    """Регистрация нового пользователя с отправкой кода подтверждения"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Создаем пользователя, но не активируем
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Удаляем старые неиспользованные коды этого пользователя
            OneTimeCode.objects.filter(user=user, is_used=False).delete()

            # Генерируем и сохраняем код подтверждения
            code = OneTimeCode.generate_code()
            verification_code = OneTimeCode.objects.create(
                user=user,
                code=code,
                is_used=False
            )

            # Сохраняем email в сессии для формы подтверждения
            request.session['verification_email'] = user.email

            # Отправляем код на email (сигнал сработает автоматически)
            messages.success(
                request,
                'Код подтверждения отправлен на вашу почту. Проверьте email и введите код.'
            )

            return redirect('accounts:verify')

        # Если форма невалидна, показываем ошибки
        return render(request, 'accounts/signup.html', {'form': form})

    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})


def verify_email(request):
    """Подтверждение email по коду"""
    email = request.session.get('verification_email')

    if not email:
        messages.error(request, 'Сессия истекла. Начните регистрацию заново.')
        return redirect('accounts:signup')

    if request.method == 'POST':
        form = VerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']

            try:
                user = User.objects.get(email=email, is_active=False)

                # Ищем действительный код
                verification_code = OneTimeCode.objects.filter(
                    user=user,
                    code=code,
                    is_used=False
                ).latest('created_at')

                if verification_code.is_valid():
                    # Активируем пользователя
                    user.is_active = True
                    user.is_verified = True
                    user.save()

                    # Помечаем код как использованный
                    verification_code.is_used = True
                    verification_code.save()

                    # Автоматически логиним пользователя
                    login(request, user)

                    # Очищаем сессию
                    del request.session['verification_email']

                    messages.success(
                        request,
                        'Email успешно подтвержден! Добро пожаловать на MMORPG Fan Board!'
                    )
                    return redirect('posts:list')
                else:
                    messages.error(request, 'Код истек или недействителен. Запросите новый код.')

                    # Опция: отправить новый код
                    if 'resend' in request.POST:
                        new_code = OneTimeCode.generate_code()
                        OneTimeCode.objects.create(user=user, code=new_code)
                        messages.info(request, 'Новый код отправлен на вашу почту.')

            except User.DoesNotExist:
                messages.error(request, 'Пользователь не найден или уже активирован.')
            except OneTimeCode.DoesNotExist:
                messages.error(request, 'Неверный код подтверждения.')
    else:
        form = VerifyForm()

    return render(request, 'accounts/verify.html', {'form': form, 'email': email})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def profile(request):
    """Профиль пользователя"""
    user_posts = request.user.posts.all()[:5]  # Последние 5 объявлений
    user_responses_count = request.user.responses.count()

    context = {
        'user': request.user,
        'user_posts': user_posts,
        'user_responses_count': user_responses_count,
    }
    return render(request, 'accounts/profile.html', context)