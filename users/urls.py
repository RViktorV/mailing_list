from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.apps import UsersConfig
from users.views import UserCreateView, email_verification, PasswordResetView, ProfileUpdateView, BlockUserView, \
    CustomPasswordChangeView, UserListView, ToggleUserStatusView

app_name = UsersConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', UserCreateView.as_view(), name='register'),
    path('email_confirm/<str:token>/', email_verification, name='email_confirm'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('profile/change-password/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/block/<int:pk>/', BlockUserView.as_view(), name='block_user'),
    path('users/toggle/<int:pk>/', ToggleUserStatusView.as_view(), name='toggle_user_status'),
]