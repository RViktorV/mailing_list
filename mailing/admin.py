from django.contrib import admin
from .models import Client, Message, Mailing, MailingAttempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name", "comment")
    list_filter = ("email",)
    search_fields = ("email", "full_name")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "body")
    search_fields = ("subject", "body")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "start_datetime", "periodicity", "status", "get_message_subject", "get_clients")
    search_fields = ("status", "periodicity", "message__subject", "clients__email")

    def get_message_subject(self, obj):
        return obj.message.subject
    get_message_subject.short_description = "Message Subject"

    def get_clients(self, obj):
        return ", ".join([client.email for client in obj.clients.all()])
    get_clients.short_description = "Clients"


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "mailing", "attempt_datetime", "status")
    search_fields = ("status", "mailing__message__subject", "mailing__clients__email")
