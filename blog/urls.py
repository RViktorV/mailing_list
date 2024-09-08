from django.urls import path
from django.views.decorators.cache import never_cache, cache_page

from .apps import BlogConfig
from .views import (
    BlogListView,
    BlogDetailView,
    BlogCreateView,
    BlogUpdateView,
    BlogDeleteView,
    BlogListViewAll,
)

app_name = BlogConfig.name

urlpatterns = [
    path('', cache_page(60*15)(BlogListView.as_view()), name='blog_list'),  # Кэш на 15 минут
    path('listAll/', cache_page(60*15)(BlogListViewAll.as_view()), name='blog_list_all'),
    path('<int:pk>/', cache_page(60*15)(BlogDetailView.as_view()), name='blog_detail'),
    path('create/', never_cache(BlogCreateView.as_view()), name='blog_create'),
    path('<int:pk>/update/', never_cache(BlogUpdateView.as_view()), name='blog_update'),
    path('<int:pk>/delete/', BlogDeleteView.as_view(), name='blog_delete'),
]
