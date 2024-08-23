from django.contrib.auth.models import User
from users.models import Users
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = Users.objects.create(email='admin@example.com')
        user.set_password('1q2w3e')
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()