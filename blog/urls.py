from django.urls import path
from django.views.decorators.cache import never_cache

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
    path('', BlogListView.as_view(), name='blog_list'),
    path('listAll/', BlogListViewAll.as_view(), name='blog_list_all'),
    path('<int:pk>/', BlogDetailView.as_view(), name='blog_detail'),
    path('create/', never_cache(BlogCreateView.as_view()), name='blog_create'),
    path('<int:pk>/update/', never_cache(BlogUpdateView.as_view()), name='blog_update'),
    path('<int:pk>/delete/', BlogDeleteView.as_view(), name='blog_delete'),
]
