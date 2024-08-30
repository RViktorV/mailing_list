from django import forms
from django.forms import ModelForm

from blog.models import Blog


class BlogForm(ModelForm):
    class Meta:
        model = Blog
        exclude = ['slug', 'view_count', 'created_at', 'updated_at']  # 22.1 - исключаем поля, которые не нужны в форме


class BlogContentManagerForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content', 'preview_image', 'is_published']
