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


class UserCreateView(CreateView):
    model = Users
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')
    template_name = 'users/user_form.html'

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f'http://{host}/users/email_confirm/{token}/'
        send_mail(
            subject="подтверждение почты",
            message=f"Добрый день, подтвердите свою почту, перейдите по ссылке{url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(Users, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


class PasswordResetView(FormView):
    template_name = 'password_reset.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        user = Users.objects.filter(email=email).first()  # Используйте вашу модель
        if user:
            new_password = get_random_string(8)  # Генерация нового пароля
            user.password = make_password(new_password)
            user.save()
            # Отправка письма с новым паролем
            send_mail(
                subject='Восстановление пароля',
                message=f'Ваш новый пароль: {new_password}',
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
        return super().form_valid(form)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'profile_edit.html'
    success_url = reverse_lazy('users:login')

    def get_object(self, queryset=None):
        return self.request.user


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'profile_edit.html'
    success_url = reverse_lazy('users:login')

