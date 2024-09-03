
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from pytils.translit import slugify

from blog.forms import BlogForm, BlogContentManagerForm
from blog.models import Blog


class BlogListViewAll(ListView):
    model = Blog


class BlogListView(ListView):
    model = Blog
    template_name = 'blog/blog_list.html'

    def get_queryset(self):
        return Blog.objects.filter(is_published=True)


class BlogDetailView(DetailView):
    model = Blog

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.view_count += 1
        obj.save()
        return obj


class BlogCreateView(CreateView):
    model = Blog
    form_class = BlogForm  # 22.1 - Формы в Django вместо fields
    success_url = reverse_lazy('blog:blog_list')

    class BlogListView(ListView):
        model = Blog  # Подставьте вашу модель
        template_name = 'blog/blog_list.html'  # Подставьте ваш шаблон

    def form_valid(self, form):
        if form.is_valid():
            new_slug = form.save()
            new_slug.slug = slugify(new_slug.title)
            new_slug.save()

        return super().form_valid(form)


class BlogUpdateView(UpdateView):
    model = Blog
    form_class = BlogForm  # 22.1 - формы в Django вместо fields
    success_url = reverse_lazy('blog:blog_list')

    def form_valid(self, form):
        if form.is_valid():
            new_slug = form.save()
            new_slug.slug = slugify(new_slug.title)
            new_slug.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:blog_detail', args=[self.kwargs.get('pk')])

    def get_form_class(self):
        user = self.request.user
        if user.has_perms([
            "blog.can_title",
            "blog.can_content",
            "blog.can_preview_image",
            "blog.can_is_published",
        ]):
            return BlogContentManagerForm
        else:
            return BlogForm
        # raise PermissionDenied


class BlogDeleteView(DeleteView):
    model = Blog
    success_url = reverse_lazy('blog:blog_list')

