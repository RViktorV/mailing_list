from django.db import models

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    objects = None
    email = models.EmailField()
    full_name = models.CharField(max_length=100, verbose_name='ФИО', help_text='Введите ФИО')
    comment = models.TextField(**NULLABLE)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

        def __str__(self):
            return self.email


class Message(models.Model):
    objects = None
    subject = models.CharField(max_length=255)
    body = models.TextField()

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

        def __str__(self):
            return self.subject


class Mailing(models.Model):
    DAILY = 'D'
    WEEKLY = 'W'
    MONTHLY = 'M'
    PERIODICITY_CHOICES = [
        (DAILY, 'Eжедневн'),
        (WEEKLY, 'Еженедельно'),
        (MONTHLY, 'Ежемесячно'),
    ]

    CREATED = 'CREATED'
    STARTED = 'STARTED'
    COMPLETED = 'COMPLETED'
    STATUS_CHOICES = [
        (CREATED, 'Созданный'),
        (STARTED, 'Начатый'),
        (COMPLETED, 'Завершенный'),
    ]

    start_datetime = models.DateTimeField()
    periodicity = models.CharField(max_length=1, choices=PERIODICITY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=CREATED)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Client)

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

        def __str__(self):
            return f"{self.message.subject} - {self.start_datetime}"


class MailingAttempt(models.Model):
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts')
    attempt_datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('success', 'Success'),
        ('failed', 'Failed')
    ])
    server_response = models.TextField(**NULLABLE)

    class Meta:
        verbose_name = 'Попытка'
        verbose_name_plural = 'Попытки'

        def __str__(self):
            return f"{self.mailing} - {self.attempt_datetime}"
