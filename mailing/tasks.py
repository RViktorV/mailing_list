import pytz
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from .models import Mailing, MailingAttempt

from apscheduler.schedulers.background import BackgroundScheduler


def send_mailing():
    """
    Эта функция проверяет рассылки, подлежащие отправке, на основе их расписания (ЕЖЕДНЕВНО, ЕЖЕНЕДЕЛЬНО, ЕЖЕМЕСЯЧНО).
    или если они не были отправлены ранее и их необходимо повторить.
    """
    zone = pytz.timezone(settings.TIME_ZONE)
    current_datetime = datetime.now(zone)

    # Обновляем статус рассылок на 'STOPPED', если время окончания прошло
    mailings_to_stop = Mailing.objects.filter(
        end_datetime__lt=current_datetime,
        status__ne=Mailing.STOPPED
    )
    for mailing in mailings_to_stop:
        mailing.status = Mailing.STOPPED
        mailing.save()

    # Получение писем, которые необходимо обработать
    mailings = Mailing.objects.filter(
        Q(start_datetime__lte=current_datetime) &
        Q(end_datetime__gte=current_datetime) &  # добавили фильтр по end_datetime
        Q(status__in=['CREATED', 'STARTED'])
    )

    for mailing in mailings:
        last_attempt = MailingAttempt.objects.filter(mailing=mailing).order_by('-attempt_datetime').first()

        if last_attempt:

            # Рассчитайте время следующей отправки на основе периодичности.
            if mailing.periodicity == 'D':
                next_send_time = last_attempt.attempt_datetime + timedelta(days=1)
            elif mailing.periodicity == 'W':
                next_send_time = last_attempt.attempt_datetime + timedelta(weeks=1)
            elif mailing.periodicity == 'M':
                next_send_time = last_attempt.attempt_datetime + timedelta(weeks=4)
            else:
                next_send_time = mailing.start_datetime  # запасной вариант, обычно он не используется
        else:
            next_send_time = mailing.start_datetime

        # Проверьте, пора ли отправлять рассылку
        if current_datetime >= next_send_time and current_datetime <= mailing.end_datetime:  # добавили проверку end_datetime
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[client.email for client in mailing.clients.all()]
                )
                # Зарегистрируйте успешную попытку
                MailingAttempt.objects.create(mailing=mailing, status='success')
                mailing.status = 'COMPLETED'  # Или обновить при необходимости
                mailing.end_datetime = current_datetime  # Обновите поле end_datetime
            except Exception as e:
                # Зарегистрируйте неудачную попытку с ответом или ошибкой сервера.
                MailingAttempt.objects.create(mailing=mailing, status='failed', server_response=str(e))
                mailing.status = 'STARTED'  # Оставьте статус «НАЧАТО», чтобы повторить попытку позже.

            mailing.save()


def start_scheduler():
    """
    Эта функция инициализирует и запускает планировщик, который будет вызывать функцию send_mailing каждые 1 минуту:
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_mailing, 'interval', minutes=1)
    scheduler.start()
