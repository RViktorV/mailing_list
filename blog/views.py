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
        return user.is_superuser or user.groups.filter(name='ContentManager').exists() or blog.owner == user

class BlogListViewAll(ListView):
    """
    Представление для отображения списка всех блогов.

    Атрибуты:
        model: Модель, которая будет отображаться. В данном случае это модель Blog.

    Методы:
        get_queryset: Возвращает все блоги.
    """
    model = Blog

class BlogListView(ListView):
    model = Blog
    template_name = 'blog/blog_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['is_content_manager'] = user.groups.filter(name='Content Manager').exists() or user.is_superuser
        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser or user.groups.filter(name='Content Manager').exists():
                return Blog.objects.all()
            else:
                return Blog.objects.filter(owner=user) | Blog.objects.filter(is_published=True)
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
    model = Blog
    form_class = BlogForm
    success_url = reverse_lazy('blog:blog_list')

    def form_valid(self, form):
        if form.is_valid():
            # Назначаем текущего пользователя владельцем блога
            new_blog = form.save(commit=False)
            new_blog.owner = self.request.user
            new_blog.slug = slugify(new_blog.title)
            new_blog.save()
        return super().form_valid(form)

class BlogUpdateView(LoginRequiredMixin, IsOwnerOrContentManagerMixin, UpdateView):
    model = Blog
    form_class = BlogForm
    success_url = reverse_lazy('blog:blog_list')

    def form_valid(self, form):
        if form.is_valid():
            # Обновляем слаг блога
            new_blog = form.save(commit=False)
            new_blog.slug = slugify(new_blog.title)
            new_blog.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:blog_detail', args=[self.kwargs.get('pk')])

    def get_form_class(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='ContentManager').exists():
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
