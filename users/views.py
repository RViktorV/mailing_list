import secrets
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.utils.crypto import get_random_string

from users.models import Users
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView

from users.forms import UserRegisterForm, PasswordResetForm, UserProfileForm

from config.settings import EMAIL_HOST_USER

from django.views.generic import FormView

from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView

from django.views import View
from django.http import HttpResponseRedirect




class UserCreateView(CreateView):
    """
    Представление для создания нового пользователя. После регистрации
    пользователь становится неактивным до подтверждения почты. На указанный
    email отправляется письмо с подтверждением и уникальной ссылкой для активации аккаунта.

    Атрибуты:
        model: модель пользователя.
        form_class: форма для регистрации пользователя.
        success_url: URL для перенаправления после успешной регистрации.
        template_name: шаблон для отображения формы регистрации.
    """
    model = Users
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')
    template_name = 'users/user_form.html'

    def form_valid(self, form):
        """
        Выполняется при успешной валидации формы. Создает пользователя, генерирует
        токен для подтверждения почты и отправляет письмо с подтверждением на email.

        Args:
            form (UserRegisterForm): валидированная форма регистрации.

        Returns:
            HttpResponse: перенаправление на success_url после отправки письма.
        """
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f'http://{host}/users/email_confirm/{token}/'
        send_mail(
            subject="подтверждение почты",
            message=f"Добрый день, подтвердите свою почту, перейдите по ссылке {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        return super().form_valid(form)


def email_verification(request, token):
    """
    Функция для подтверждения email пользователя. Активирует учетную запись
    пользователя после подтверждения ссылки с токеном.

    Args:
        request (HttpRequest): текущий запрос.
        token (str): токен, переданный в URL для подтверждения почты.

    Returns:
        HttpResponse: перенаправление на страницу входа после успешного подтверждения.
    """
    user = get_object_or_404(Users, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


class PasswordResetView(FormView):
    """
    Представление для сброса пароля. При вводе email, если пользователь найден,
    генерируется новый случайный пароль, который отправляется на email пользователя.

    Атрибуты:
        template_name: шаблон для отображения формы сброса пароля.
        form_class: форма для сброса пароля.
        success_url: URL для перенаправления после успешной отправки письма.
    """
    template_name = 'password_reset.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        """
        Выполняется при успешной валидации формы. Проверяет email в базе данных,
        генерирует новый пароль и отправляет его на почту пользователя.

        Args:
            form (PasswordResetForm): валидированная форма сброса пароля.

        Returns:
            HttpResponse: перенаправление на success_url после отправки письма.
        """
        email = form.cleaned_data['email']
        user = Users.objects.filter(email=email).first()
        if user:
            new_password = get_random_string(8)
            user.password = make_password(new_password)
            user.save()
            send_mail(
                subject='Восстановление пароля',
                message=f'Ваш новый пароль: {new_password}',
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
        return super().form_valid(form)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для обновления профиля пользователя. Пользователь должен быть
    авторизован для доступа к форме редактирования профиля.

    Атрибуты:
        model: модель пользователя.
        form_class: форма для редактирования профиля пользователя.
        template_name: шаблон для отображения формы редактирования профиля.
        success_url: URL для перенаправления после успешного редактирования профиля.
    """
    model = User
    form_class = UserProfileForm
    template_name = 'profile_edit.html'
    success_url = reverse_lazy('users:login')

    def get_object(self, queryset=None):
        """
        Возвращает текущего пользователя для редактирования его профиля.

        Returns:
            User: объект текущего авторизованного пользователя.
        """
        return self.request.user


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    Представление для смены пароля пользователя. Пользователь должен быть авторизован
    для доступа к форме смены пароля.

    Атрибуты:
        template_name: шаблон для отображения формы смены пароля.
        success_url: URL для перенаправления после успешной смены пароля.
    """
    template_name = 'profile_edit.html'
    success_url = reverse_lazy('users:login')


class UserListView(UserPassesTestMixin, ListView):
    model = Users
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.groups.filter(name='Moderator').exists()

    def handle_no_permission(self):
        return redirect('home')  # Перенаправление на дом, если вы не модератор


class BlockUserView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.groups.filter(name='Moderator').exists()

    def post(self, request, pk):
        user = get_object_or_404(Users, pk=pk)
        user.is_active = False
        user.save()
        return HttpResponseRedirect(reverse('users:user_list'))


class ToggleUserStatusView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.groups.filter(name='Moderator').exists()

    def post(self, request, pk):
        user = get_object_or_404(Users, pk=pk)
        # Переключить статус is_active
        user.is_active = not user.is_active
        user.save()
        return HttpResponseRedirect(reverse('users:user_list'))