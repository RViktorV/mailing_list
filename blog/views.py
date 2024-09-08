from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from pytils.translit import slugify

from blog.forms import BlogForm, BlogContentManagerForm
from blog.models import Blog

class IsOwnerOrContentManagerMixin(UserPassesTestMixin):
    """
    Миксин для проверки прав доступа к объектам блога.

    Проверяет, является ли пользователь владельцем блога или контент-менеджером.
    Доступ разрешен:
    - Суперпользователям
    - Пользователям из группы 'Content Manager'
    - Владельцу объекта блога

    Методы:
        test_func: Определяет, имеет ли пользователь доступ к объекту.
    """

    def test_func(self):
        user = self.request.user
        blog = self.get_object()
        return user.is_superuser or user.groups.filter(name='Content Manager').exists() or blog.owner == user

class BlogListViewAll(ListView):
    """
    Представление для отображения списка всех блогов, включая неопубликованные.

    Атрибуты:
        model: Модель, которая будет отображаться. В данном случае это модель Blog.

    Методы:
        get_queryset: Возвращает все блоги для аутентифицированных пользователей и владельцев.
    """
    model = Blog

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser or user.groups.filter(name='Content Manager').exists():
                return Blog.objects.all()
            return Blog.objects.filter(owner=user)
        return Blog.objects.none()

class BlogListView(ListView):
    """
    Представление для отображения списка опубликованных блогов.

    Атрибуты:
        model: Модель, которая будет отображаться. В данном случае это модель Blog.
        template_name: Шаблон для отображения списка опубликованных блогов.

    Методы:
        get_queryset: Возвращает только опубликованные блоги для аутентифицированных пользователей и владельцев.
    """
    model = Blog
    template_name = 'blog/blog_list.html'

    def get_queryset(self):
        if self.request.user.is_authenticated and not self.request.user.is_superuser and not self.request.user.groups.filter(name='Content Manager').exists():
            return Blog.objects.filter(is_published=True, owner=self.request.user)
        return Blog.objects.filter(is_published=True)

class BlogDetailView(DetailView):
    """
    Представление для отображения детальной информации о блоге.

    Атрибуты:
        model: Модель, которая будет отображаться. В данном случае это модель Blog.

    Методы:
        get_object: Увеличивает счетчик просмотров при каждом обращении к объекту блога и возвращает его.
    """
    model = Blog

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.view_count += 1
        obj.save()
        return obj

class BlogCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания нового блога.

    Атрибуты:
        model: Модель, для которой создается новый объект. В данном случае это модель Blog.
        form_class: Форма для создания блога.
        success_url: URL для перенаправления после успешного создания блога.

    Методы:
        form_valid: Устанавливает владельца блога и сохраняет объект с новым слагом.
    """
    model = Blog
    form_class = BlogForm
    success_url = reverse_lazy('blog:blog_list')

    def form_valid(self, form):
        if form.is_valid():
            new_blog = form.save(commit=False)
            new_blog.owner = self.request.user
            new_blog.save()
            new_blog.slug = slugify(new_blog.title)
            new_blog.save()
        return super().form_valid(form)

class BlogUpdateView(LoginRequiredMixin, IsOwnerOrContentManagerMixin, UpdateView):
    """
    Представление для обновления существующего блога.

    Атрибуты:
        model: Модель, для которой выполняется обновление. В данном случае это модель Blog.
        form_class: Форма для редактирования блога.
        success_url: URL для перенаправления после успешного обновления блога.

    Методы:
        form_valid: Обновляет слаг блога и сохраняет изменения.
        get_success_url: Возвращает URL для перенаправления после успешного обновления.
        get_form_class: Возвращает класс формы в зависимости от прав пользователя.
    """
    model = Blog
    form_class = BlogForm
    success_url = reverse_lazy('blog:blog_list')

    def form_valid(self, form):
        if form.is_valid():
            new_blog = form.save(commit=False)
            new_blog.slug = slugify(new_blog.title)
            new_blog.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:blog_detail', args=[self.kwargs.get('pk')])

    def get_form_class(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Content Manager').exists():
            return BlogContentManagerForm
        else:
            return BlogForm

class BlogDeleteView(LoginRequiredMixin, IsOwnerOrContentManagerMixin, DeleteView):
    """
    Представление для удаления блога.

    Атрибуты:
        model: Модель, для которой выполняется удаление. В данном случае это модель Blog.
        success_url: URL для перенаправления после успешного удаления блога.

    Методы:
        get_queryset: Возвращает все блоги для удаления, если пользователь суперпользователь или контент-менеджер; иначе, только блоги владельца.
    """
    model = Blog
    success_url = reverse_lazy('blog:blog_list')
