from datetime import timedelta

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import render, get_object_or_404

from blog.models import Blog
from .forms import MailingForm, ClientForm, MessageForm, MailingAttemptForm
from .models import Client, Message, Mailing, MailingAttempt


def home(request):
    """
    Отображает главную страницу с краткой информацией о рассылках и случайными блогами.

    Шаблон: base.html
    Контекст:
    - mailings_count: Общее количество рассылок.
    - mailings_count_active: Количество активных рассылок (кроме остановленных).
    - clients_count: Количество уникальных клиентов.
    - articles: Случайные три блога.
    """
    mailings = Mailing.objects.all()
    blogs = Blog.objects.order_by("?")[:3]  # Получаем случайные блоги

    context = {
        "mailings_count": mailings.count(),
        "mailings_count_active": mailings.exclude(status=Mailing.CREATED).count(),
        "clients_count": Client.objects.all().values("email").distinct().count(),
        "articles": blogs,  # Передаём блоги в контекст
    }

    return render(request, "base.html", context)


from django.contrib.auth.mixins import UserPassesTestMixin

class CanViewAttemptsMixin(UserPassesTestMixin):
    """
    Миксин для проверки прав доступа к списку попыток рассылки.
    Пользователь может просматривать попытки рассылки, если он является:
    1. Владельцем соответствующих рассылок.
    2. Членом группы 'Moderator'.
    """

    def test_func(self):
        # Проверяем, что пользователь является суперпользователем или членом группы 'Moderator'
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Moderator').exists():
            return True

        # Получаем queryset попыток рассылки
        queryset = self.get_queryset()

        # Проверяем, что хотя бы один объект в queryset принадлежит текущему пользователю
        return queryset.filter(mailing__owner=self.request.user).exists()


class IsOwnerOrModeratorMixin(UserPassesTestMixin):
    """
    Миксин, чтобы проверить, является ли пользователь владельцем, суперпользователем или членом группы «Модератор».
    """
    def test_func(self):
        mailing = get_object_or_404(Mailing, pk=self.kwargs.get('pk'))
        return (self.request.user == mailing.owner or
                self.request.user.is_superuser or
                self.request.user.groups.filter(name='Moderator').exists())


class IsManagerMixin(UserPassesTestMixin):
    """
    Миксин для проверки, входит ли пользователь в группу 'Moderator'.
    """

    def test_func(self):
        return self.request.user.groups.filter(name='Moderator').exists()


class CanViewMailingsMixin(UserPassesTestMixin):
    """
    Миксин для проверки, имеет ли пользователь права на просмотр рассылок.
    Пользователь может просматривать рассылку, если он суперпользователь, менеджер (входит в группу 'Moderator')
    или является владельцем рассылки (owner).
    """

    def test_func(self):
        mailing = self.get_object()  # Получаем объект рассылки
        # Проверка: пользователь суперпользователь, менеджер или владелец рассылки
        return (self.request.user.is_superuser or
                self.request.user.groups.filter(name='Moderator').exists() or
                mailing.owner == self.request.user)


class CanDeactivateMailingsMixin(UserPassesTestMixin):
    """
    Миксин для проверки, имеет ли пользователь права на деактивацию рассылок.
    """

    def test_func(self):
        return self.request.user.has_perm('mailing.deactivate-mailings')


class IsOwnerOrSuperuserMixin(UserPassesTestMixin):
    """
    Миксин для проверки прав на редактирование и удаление рассылок.
    Пользователь может редактировать или удалять рассылки, если он является владельцем или суперпользователем.
    """
    def test_func(self):
        mailing = get_object_or_404(Mailing, pk=self.kwargs.get('pk'))
        return self.request.user == mailing.owner or self.request.user.is_superuser


class MailingDeactivateView(CanDeactivateMailingsMixin, UpdateView):
    """
    Представление для деактивации рассылки.

    Шаблон: mailings/mailing_deactivate.html
    """
    model = Mailing
    fields = ['status']
    template_name = 'mailings/mailing_deactivate.html'
    success_url = reverse_lazy('mailing:mailing-list')

    def form_valid(self, form):
        """
        При успешной отправке формы статус рассылки устанавливается на 'Завершено'.
        """
        form.instance.status = Mailing.COMPLETED  # Или другой статус для деактивации
        return super().form_valid(form)


class ClientListView(LoginRequiredMixin, ListView):
    """
    Представление для отображения списка клиентов.

    Шаблон: clients/client_list.html
    """
    model = Client
    template_name = "clients/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        """
        Возвращает клиентов: суперпользователь видит всех, обычный пользователь видит только своих.
        """
        if self.request.user.is_superuser:
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(CreateView):
    """
    Представление для создания нового клиента.

    Шаблон: clients/client_form.html
    """
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('mailing:client-list')

    def form_valid(self, form):
        """
        Устанавливает текущего пользователя владельцем клиента.
        """
        client = form.save(commit=False)
        client.owner = self.request.user
        client.save()
        return super().form_valid(form)


class ClientUpdateView(CanViewMailingsMixin, UpdateView):
    """
    Представление для обновления клиента.

    Шаблон: clients/client_form.html
    """
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('mailing:client-list')

    def get_queryset(self):
        """
        Суперпользователь может редактировать всех клиентов, обычный пользователь — только своих.
        """
        if self.request.user.is_superuser:
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientDeleteView(CanViewMailingsMixin, DeleteView):
    """
    Представление для удаления клиента.

    Шаблон: clients/client_confirm_delete.html
    """
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('mailing:client-list')

    def get_queryset(self):
        """
        Суперпользователь может удалять всех клиентов, обычный пользователь — только своих.
        """
        if self.request.user.is_superuser:
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class MessageListView(LoginRequiredMixin, ListView):
    """
    Представление для отображения списка сообщений.

    Шаблон: message/message_list.html
    """
    model = Message
    template_name = "message/message_list.html"
    context_object_name = "message"

    def get_queryset(self):
        """
        Суперпользователь видит все сообщения, обычные пользователи видят только свои.
        """
        if self.request.user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(CreateView):
    """
    Представление для создания нового сообщения.

    Шаблон: message/message_form.html
    """
    model = Message
    form_class = MessageForm
    template_name = 'message/message_form.html'
    success_url = reverse_lazy('mailing:message-list')

    def form_valid(self, form):
        """
        Устанавливает текущего пользователя владельцем сообщения.
        """
        message = form.save(commit=False)
        message.owner = self.request.user
        message.save()
        return super().form_valid(form)


class MessageUpdateView(CanViewMailingsMixin, UpdateView):
    """
    Представление для обновления сообщения.

    Шаблон: message/message_form.html
    """
    model = Message
    form_class = MessageForm
    template_name = 'message/message_form.html'
    success_url = reverse_lazy('mailing:message-list')

    def get_queryset(self):
        """
        Суперпользователь может редактировать все сообщения, обычные пользователи — только свои.
        """
        if self.request.user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageDeleteView(CanViewMailingsMixin, DeleteView):
    """
    Представление для удаления сообщения.

    Шаблон: message/message_confirm_delete.html
    """
    model = Message
    template_name = 'message/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message-list')

    def get_queryset(self):
        """
        Суперпользователь может удалять все сообщения, обычные пользователи — только свои.
        """
        if self.request.user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MailingListView(LoginRequiredMixin, ListView):
    """
    Представление для отображения списка рассылок.

    Шаблон: mailings/mailing_list.html
    """
    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        """
        Модераторы и суперпользователи могут видеть все рассылки,
        обычные пользователи могут видеть только свои.
        """
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Moderator').exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(CreateView):
    """
    Представление для создания новой рассылки.

    Шаблон: mailings/mailing_form.html
    """
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing-list')

    def form_valid(self, form):
        """
        Устанавливает текущего пользователя владельцем рассылки и сохраняет её.
        Если время окончания не указано, оно автоматически устанавливается на один день позже времени начала.
        """
        mailing = form.save(commit=False)
        mailing.owner = self.request.user
        if not mailing.end_datetime:
            mailing.end_datetime = mailing.start_datetime + timedelta(days=1)
        mailing.save()
        return super().form_valid(form)


class MailingUpdateView(IsOwnerOrModeratorMixin, UpdateView):
    """
   Просмотр обновления рассылок.
   """
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.groups.filter(name='Moderator').exists():
            if self.object.owner != self.request.user:
                # Если рассылка не принадлежит модератору, разрешите редактирование только поля статуса.
                form.fields['status'].disabled = False
                form.fields['start_datetime'].disabled = True
                form.fields['end_datetime'].disabled = True
                form.fields['periodicity'].disabled = True
                form.fields['message'].disabled = True
                form.fields['clients'].disabled = True
            else:
                # Если рассылка принадлежит модератору, разрешите редактирование всех полей
                form.fields['status'].disabled = False
                form.fields['start_datetime'].disabled = False
                form.fields['end_datetime'].disabled = False
                form.fields['periodicity'].disabled = False
                form.fields['message'].disabled = False
                form.fields['clients'].disabled = False
        return form

class MailingDeleteView(IsOwnerOrSuperuserMixin, DeleteView):
    """
    Представление для удаления рассылки.
    """
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing-list')


class AttemptListView(CanViewAttemptsMixin, ListView):
    """
    Представление для отображения списка попыток рассылки.

    Суперпользователь видит все попытки рассылки. Менеджеры также видят все попытки.
    Обычные пользователи могут видеть только попытки рассылок, которые им принадлежат.

    Атрибуты:
        model: Модель, которая будет отображаться. В данном случае это модель MailingAttempt.
        template_name: Шаблон для отображения списка попыток рассылки.
        context_object_name: Имя переменной в контексте шаблона, под которой будут доступны попытки.

    Методы:
        get_queryset: Возвращает список попыток, доступных для просмотра текущему пользователю.
    """
    model = MailingAttempt
    template_name = 'attempt/attempt_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        """Возвращает все попытки для суперпользователя или менеджеров, либо только попытки текущего пользователя."""
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Moderator').exists():
            return MailingAttempt.objects.all()

        # Возвращаем попытки рассылки, принадлежащие текущему пользователю
        return MailingAttempt.objects.filter(mailing__owner=self.request.user)
