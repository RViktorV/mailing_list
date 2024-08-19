from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from mailing.tasks import send_mailing


class Command(BaseCommand):
    help = 'Send scheduled mailings'

    def handle(self, *args, **kwargs):
        send_mailing()
        self.stdout.write(self.style.SUCCESS('Successfully sent mailings'))
