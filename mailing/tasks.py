import pytz
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.core.mail import send_mail
from .models import Mailing, MailingAttempt

def send_mailing():
    zone = pytz.timezone(settings.TIME_ZONE)
    current_datetime = datetime.now(zone)
    mailings = Mailing.objects.filter(send_date__lte=current_datetime).filter(
        status__in=['pending', 'scheduled'])

    for mailing in mailings:
        last_attempt = MailingAttempt.objects.filter(mailing=mailing).order_by('-attempt_date').first()
        if last_attempt:
            time_since_last_attempt = current_datetime - last_attempt.attempt_date
            if mailing.periodicity == 'daily' and time_since_last_attempt.days < 1:
                continue
            next_send_time = last_attempt.attempt_date + timedelta(days=1)
        else:
            next_send_time = mailing.send_date

        if current_datetime >= next_send_time:
            send_mail(
                subject=mailing.subject,
                message=mailing.text,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[client.email for client in mailing.clients.all()]
            )
            MailingAttempt.objects.create(mailing=mailing, attempt_date=current_datetime)
            mailing.status = 'sent'
            mailing.save()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_mailing, 'interval', minutes=1)
    scheduler.start()
