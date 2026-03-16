# responses/views.py
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .models import Response
from posts.models import Post


class UserResponsesView(LoginRequiredMixin, ListView):
    """Страница с откликами на объявления пользователя"""
    model = Response
    template_name = 'responses/user_responses.html'
    context_object_name = 'responses'
    paginate_by = 20

    def get_queryset(self):
        # Берем все отклики на посты текущего пользователя
        queryset = Response.objects.filter(post__author=self.request.user)

        # Фильтр по конкретному объявлению
        post_id = self.request.GET.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)

        # Фильтр по статусу
        status = self.request.GET.get('status')
        if status == 'accepted':
            queryset = queryset.filter(is_accepted=True)
        elif status == 'pending':
            queryset = queryset.filter(is_accepted=False)

        # Поиск по тексту отклика
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(text__icontains=search)

        return queryset.select_related('author', 'post').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Список постов пользователя для фильтрации
        context['user_posts'] = Post.objects.filter(author=self.request.user)

        # Текущие параметры фильтрации
        context['current_post'] = self.request.GET.get('post', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')

        return context


@login_required
def accept_response(request, pk):
    """Принять отклик (только автор поста)"""
    response = get_object_or_404(Response, pk=pk)

    # Проверяем, что текущий пользователь - автор поста
    if response.post.author != request.user:
        raise PermissionDenied("Вы не можете принять этот отклик")

    if not response.is_accepted:
        response.is_accepted = True
        response.save()
        messages.success(request, 'Отклик принят. Уведомление отправлено автору отклика.')
    else:
        messages.info(request, 'Отклик уже был принят ранее')

    return redirect('responses:user_responses')


@login_required
def delete_response(request, pk):
    """Удалить отклик (только автор поста)"""
    response = get_object_or_404(Response, pk=pk)

    # Проверяем, что текущий пользователь - автор поста
    if response.post.author != request.user:
        raise PermissionDenied("Вы не можете удалить этот отклик")

    response.delete()
    messages.success(request, 'Отклик удален')
    return redirect('responses:user_responses')