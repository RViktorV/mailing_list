from django import forms
from .models import Client, Message, Mailing, MailingAttempt

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Введите ФИО'}),
            'comment': forms.Textarea(attrs={'placeholder': 'Оставьте комментарий'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Тема сообщения'}),
            'body': forms.Textarea(attrs={'placeholder': 'Текст сообщения'}),
        }

class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_datetime', 'periodicity', 'status', 'message', 'clients']
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'periodicity': forms.Select(),
            'status': forms.Select(),
            'message': forms.Select(),
            'clients': forms.CheckboxSelectMultiple(),
        }

class MailingAttemptForm(forms.ModelForm):
    class Meta:
        model = MailingAttempt
        fields = ['mailing', 'status', 'server_response']
        widgets = {
            'mailing': forms.Select(),
            'status': forms.Select(),
            'server_response': forms.Textarea(attrs={'placeholder': 'Ответ сервера'}),
        }
