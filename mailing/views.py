from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import MailingForm, AttemptForm
from .models import Client, Message, Mailing, MailingAttempt
from django.shortcuts import render


def home(request):
    return render(request, 'base.html')


class ClientListView(ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'


class ClientCreateView(CreateView):
    model = Client
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('mailing:client-list')
    fields = ['email', 'full_name', 'comment']


class ClientUpdateView(UpdateView):
    model = Client
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('mailing:client-list')
    fields = ['email', 'full_name', 'comment']


class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('mailing:client-list')


class MessageListView(ListView):
    model = Message
    template_name = 'message/message_list.html'
    context_object_name = 'messages'


class MessageCreateView(CreateView):
    model = Message
    template_name = 'message/message_form.html'
    success_url = reverse_lazy('mailing:message-list')
    fields = ['subject', 'body']


class MessageUpdateView(UpdateView):
    model = Message
    template_name = 'message/message_form.html'
    success_url = reverse_lazy('mailing:message-list')
    fields = ['subject', 'body']


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'message/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message-list')
    fields = ['subject', 'body']


class MailingListView(ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing-list')
    # fields = ['start_datetime', 'periodicity', 'message', 'clients']


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing-list')
    # fields = ['start_datetime', 'periodicity', 'message', 'clients']


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing-list')


class AttemptListView(ListView):
    model = MailingAttempt
    form_class = AttemptForm
    template_name = 'attempt/attempt_list.html'
    context_object_name = 'attempts'
    success_url = reverse_lazy('mailing:mailing-list')
