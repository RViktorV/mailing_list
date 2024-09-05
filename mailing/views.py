from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import render

from blog.models import Blog
from .forms import MailingForm, ClientForm, MessageForm, MailingAttemptForm
from .models import Client, Message, Mailing, MailingAttempt

import random

def home(request):
    """Главная страница"""

    mailings = Mailing.objects.all()
    blogs = Blog.objects.order_by("?")[:3]  # Получаем случайные блоги

    context = {
        "mailings_count": mailings.count(),
        "mailings_count_active": mailings.exclude(status=Mailing.STOPPED).count(),
        "clients_count": Client.objects.all().values("email").distinct().count(),
        "articles": blogs,  # Передаём блоги в контекст
    }

    return render(request, "base.html", context)

class IsSuperuserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class IsManagerMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Moderator').exists()


class CanViewMailingsMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Moderator').exists()


class CanDeactivateMailingsMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.has_perm('mailing.deactivate-mailings')


class MailingDeactivateView(CanDeactivateMailingsMixin, UpdateView):
    model = Mailing
    fields = ['status']
    template_name = 'mailings/mailing_deactivate.html'
    success_url = reverse_lazy('mailing:mailing-list')

    def form_valid(self, form):
        form.instance.status = Mailing.COMPLETED  # Или другой статус для деактивации
        return super().form_valid(form)


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "clients/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        queryset = super().get_queryset().filter(owner=self.request.user)
        if not queryset.exists():
            self.extra_context = {'no_clients': True}
        return queryset


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('mailing:client-list')

    def form_valid(self, form):
        client = form.save(commit=False)
        client.owner = self.request.user
        client.save()
        return super().form_valid(form)


class ClientUpdateView(IsSuperuserMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('mailing:client-list')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientDeleteView(IsSuperuserMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('mailing:client-list')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "message/message_list.html"
    context_object_name = "message"

    def get_queryset(self):
        queryset = super().get_queryset().filter(owner=self.request.user)
        if not queryset.exists():
            self.extra_context = {'no_messages': True}
        return queryset


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'message/message_form.html'
    success_url = reverse_lazy('mailing:message-list')

    def form_valid(self, form):
        message = form.save(commit=False)
        message.owner = self.request.user
        message.save()
        return super().form_valid(form)


class MessageUpdateView(IsSuperuserMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'message/message_form.html'
    success_url = reverse_lazy('mailing:message-list')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageDeleteView(IsSuperuserMixin, DeleteView):
    model = Message
    template_name = 'message/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message-list')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        queryset = super().get_queryset().filter(owner=self.request.user)
        if not queryset.exists():
            self.extra_context = {'no_mailings': True}
        return queryset


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing-list')

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.owner = self.request.user
        mailing.save()
        return super().form_valid(form)


# class MailingUpdateView(IsSuperuserMixin, UpdateView):
#     model = Mailing
#     form_class = MailingForm
#     template_name = 'mailings/mailing_form.html'
#     success_url = reverse_lazy('mailing:mailing-list')
#
#     def get_queryset(self):
#         return Mailing.objects.all()
#
#
# class MailingDeleteView(IsSuperuserMixin, DeleteView):
#     model = Mailing
#     template_name = 'mailings/mailing_confirm_delete.html'
#     success_url = reverse_lazy('mailing:mailing-list')
#
#     def get_queryset(self):
#         return Mailing.objects.all()


class MailingUpdateView(IsSuperuserMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing-list')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)

class MailingDeleteView(IsSuperuserMixin, DeleteView):
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing-list')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)

class AttemptListView(CanViewMailingsMixin, ListView):
    model = MailingAttempt
    template_name = 'attempt/attempt_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return MailingAttempt.objects.all()
        if self.request.user.groups.filter(name='Moderator').exists():
            return MailingAttempt.objects.all()
        return MailingAttempt.objects.filter(mailing__owner=self.request.user)

# from django.urls import reverse_lazy
# from django.views.generic import ListView, CreateView, UpdateView, DeleteView
#
# from .forms import MailingForm, ClientForm, MessageForm, MailingAttemptForm
# from .models import Client, Message, Mailing, MailingAttempt
# from django.shortcuts import render
#
#
# def home(request):
#     return render(request, 'base.html')
#
#
# class ClientListView(ListView):
#     model = Client
#     form_class = ClientForm
#     template_name = 'clients/client_list.html'
#     context_object_name = 'clients'
#
#
# class ClientCreateView(CreateView):
#     model = Client
#     form_class = ClientForm
#     template_name = 'clients/client_form.html'
#     success_url = reverse_lazy('mailing:client-list')
#
#     def form_valid(self, form):
#         client = form.save()
#         user = self.request.user
#         client.owner = user
#         client.save()
#         return super().form_valid(form)
#
#
# class ClientUpdateView(UpdateView):
#     model = Client
#     form_class = ClientForm
#     template_name = 'clients/client_form.html'
#     success_url = reverse_lazy('mailing:client-list')
#
#
# class ClientDeleteView(DeleteView):
#     model = Client
#     template_name = 'clients/client_confirm_delete.html'
#     success_url = reverse_lazy('mailing:client-list')
#
#
# class MessageListView(ListView):
#     model = Message
#     template_name = 'message/message_list.html'
#     context_object_name = 'message'
#
#
# class MessageCreateView(CreateView):
#     model = Message
#     form_class = MessageForm
#     template_name = 'message/message_form.html'
#     success_url = reverse_lazy('mailing:message-list')
#
#     def form_valid(self, form):
#         message = form.save()
#         user = self.request.user
#         message.owner = user
#         message.save()
#         return super().form_valid(form)
#
#
# class MessageUpdateView(UpdateView):
#     model = Message
#     form_class = MessageForm
#     template_name = 'message/message_form.html'
#     success_url = reverse_lazy('mailing:message-list')
#
#
# class MessageDeleteView(DeleteView):
#     model = Message
#     template_name = 'message/message_confirm_delete.html'
#     success_url = reverse_lazy('mailing:message-list')
#
#
# class MailingListView(ListView):
#     model = Mailing
#     form_class = MailingForm
#     template_name = 'mailings/mailing_list.html'
#     context_object_name = 'mailings'
#
#
# class MailingCreateView(CreateView):
#     model = Mailing
#     form_class = MailingForm
#     template_name = 'mailings/mailing_form.html'
#     success_url = reverse_lazy('mailing:mailing-list')
#
#     def form_valid(self, form):
#         mailing = form.save()
#         user = self.request.user
#         mailing.owner = user
#         mailing.save()
#         return super().form_valid(form)
#
#
# class MailingUpdateView(UpdateView):
#     model = Mailing
#     form_class = MailingForm
#     template_name = 'mailings/mailing_form.html'
#     success_url = reverse_lazy('mailing:mailing-list')
#
#
# class MailingDeleteView(DeleteView):
#     model = Mailing
#     template_name = 'mailings/mailing_confirm_delete.html'
#     success_url = reverse_lazy('mailing:mailing-list')
#
#
# class AttemptListView(ListView):
#     model = MailingAttempt
#     form_class = MailingAttemptForm
#     template_name = 'attempt/attempt_list.html'
#     context_object_name = 'attempts'
#     success_url = reverse_lazy('mailing:mailing-list')
