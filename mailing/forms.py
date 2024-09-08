from django import forms
from .models import Client, Message, Mailing, MailingAttempt

class ClientForm(forms.ModelForm):
    """
    Форма для создания и редактирования клиента.

    Атрибуты:
        model: Указывает модель, с которой связана форма (Client).
        fields: Поля модели, которые будут доступны для редактирования.
        widgets: Виджеты, используемые для отображения полей формы с предустановленными атрибутами, такими как плейсхолдеры.
    """
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Введите ФИО'}),
            'comment': forms.Textarea(attrs={'placeholder': 'Оставьте комментарий'}),
        }


class ClientModeratorForm(forms.ModelForm):
    """
    Упрощенная форма для модераторов, позволяющая редактировать только поле полного имени клиента.

    Атрибуты:
        model: Указывает модель, с которой связана форма (Client).
        fields: Содержит только поле 'full_name', которое модератор может редактировать.
    """
    class Meta:
        model = Client
        fields = ['full_name']


class MessageForm(forms.ModelForm):
    """
    Форма для создания и редактирования сообщения.

    Атрибуты:
        model: Указывает модель, с которой связана форма (Message).
        fields: Поля модели, которые будут доступны для редактирования.
        widgets: Виджеты для полей формы с предустановленными плейсхолдерами для облегчения ввода данных.
    """
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Тема сообщения'}),
            'body': forms.Textarea(attrs={'placeholder': 'Текст сообщения'}),
        }


class MailingForm(forms.ModelForm):
    """
    Форма для создания и редактирования рассылки.

    Атрибуты:
        model: Указывает модель, с которой связана форма (Mailing).
        fields: Поля модели, которые будут доступны для редактирования (дата начала, периодичность, статус, сообщение, клиенты).
        widgets: Виджеты для отображения полей формы, включая выбор даты и времени, выпадающие списки и множественный выбор.
    """
    class Meta:
        model = Mailing
        fields = ['start_datetime', 'end_datetime', 'periodicity', 'status', 'message', 'clients']
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'periodicity': forms.Select(),
            'status': forms.Select(),
            'message': forms.Select(),
            'clients': forms.CheckboxSelectMultiple(),
        }


class MailingAttemptForm(forms.ModelForm):
    """
    Форма для создания и редактирования попытки рассылки.

    Атрибуты:
        model: Указывает модель, с которой связана форма (MailingAttempt).
        fields: Поля модели, которые будут доступны для редактирования (рассылка, статус, ответ сервера).
        widgets: Виджеты для отображения полей формы, включая выпадающие списки и текстовое поле для ответа сервера.
    """
    class Meta:
        model = MailingAttempt
        fields = ['mailing', 'status', 'server_response']
        widgets = {
            'mailing': forms.Select(),
            'status': forms.Select(),
            'server_response': forms.Textarea(attrs={'placeholder': 'Ответ сервера'}),
        }
