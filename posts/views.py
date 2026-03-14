# posts/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Post, Category
from .forms import PostForm
from responses.forms import ResponseForm
from responses.models import Response


class PostListView(ListView):
    """Список всех объявлений с фильтрацией по категориям"""
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Фильтр по категории
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__name=category)

        # Поиск по заголовку и тексту
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )

        return queryset.select_related('author', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class PostDetailView(DetailView):
    """Детальный просмотр объявления с формой отклика"""
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Форма для отклика (только для авторизованных)
        if self.request.user.is_authenticated:
            context['response_form'] = ResponseForm()

        # Отклики (с проверкой прав)
        if self.request.user == self.object.author:
            # Автор видит все отклики
            context['responses'] = self.object.responses.select_related('author').all()
        else:
            # Другие пользователи видят только принятые отклики
            context['responses'] = self.object.responses.filter(
                is_accepted=True
            ).select_related('author')

        return context

    def post(self, request, *args, **kwargs):
        """Обработка отклика"""
        if not request.user.is_authenticated:
            messages.error(request, 'Чтобы оставить отклик, войдите в систему')
            return redirect('accounts:login')

        self.object = self.get_object()
        form = ResponseForm(request.POST)

        if form.is_valid():
            response = form.save(commit=False)
            response.post = self.object
            response.author = request.user
            response.save()

            messages.success(request, 'Отклик успешно отправлен!')

            # TODO: Отправить уведомление автору поста (будет в сигналах)

        else:
            messages.error(request, 'Ошибка при отправке отклика')

        return redirect('posts:detail', pk=self.object.pk)


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового объявления"""
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('posts:list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Объявление успешно создано!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание объявления'
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование объявления"""
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_success_url(self):
        messages.success(self.request, 'Объявление успешно обновлено!')
        return reverse_lazy('posts:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование объявления'
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление объявления"""
    model = Post
    success_url = reverse_lazy('posts:list')
    template_name = 'posts/post_confirm_delete.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Объявление успешно удалено!')
        return super().delete(request, *args, **kwargs)
