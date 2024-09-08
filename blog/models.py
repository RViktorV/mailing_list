from django.db import models
from django.utils.text import slugify

from config import settings

NULLABLE = {'null': True, 'blank': True}


class Blog(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=3)
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.CharField(unique=True, max_length=200, verbose_name="Ссылка")
    content = models.TextField(verbose_name="Содержимое")
    preview_image = models.ImageField(upload_to='blog/', **NULLABLE, verbose_name="Превью")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Просмотры")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Блог'
        verbose_name_plural = 'Блоги'
        permissions = [
            ("can_title", "Можно менять заголовок"),
            ("can_content", "Можно менять описание"),
            ("can_preview_image", "Можно менять изображение к блогу"),
            ("can_is_published", "Можно отменять публикацию"),

        ]

