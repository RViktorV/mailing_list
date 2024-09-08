from django.db import models
from users.models import Users

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    """
    Модель, представляющая клиента сервиса.

    Атрибуты:
    - email (EmailField): Адрес электронной почты клиента.
    - full_name (CharField): Полное имя клиента (ФИО).
    - comment (TextField): Комментарий о клиенте. Может быть пустым.
    - owner (ForeignKey): Владелец клиента, связанный с моделью пользователя (Users). Может быть пустым.
    """
    objects = None
    email = models.EmailField()
    full_name = models.CharField(max_length=100, verbose_name='ФИО', help_text='Введите ФИО')
    comment = models.TextField(**NULLABLE)
    owner = models.ForeignKey(Users, verbose_name='Собственник клиента', **NULLABLE, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        permissions = [
            ("watch-list-client", "Может просматривать список пользователей сервиса."),
        ]

    def __str__(self):
        return self.email


class Message(models.Model):
    """
    Модель, представляющая сообщение для рассылки.

    Атрибуты:
    - subject (CharField): Тема сообщения.
    - body (TextField): Тело сообщения.
    - owner (ForeignKey): Владелец сообщения, связанный с моделью пользователя (Users). Может быть пустым.
    """
    objects = None
    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(Users, verbose_name='Собственник сообщения', **NULLABLE, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """
    Модель, представляющая рассылку.

    Атрибуты:
    - start_datetime (DateTimeField): Дата и время начала рассылки.
    - end_datetime (DateTimeField): Дата и время окончания рассылки.
    - periodicity (CharField): Периодичность рассылки (ежедневная, еженедельная, ежемесячная).
    - status (CharField): Статус рассылки (создана, начата, завершена).
    - message (ForeignKey): Сообщение, связанное с рассылкой.
    - clients (ManyToManyField): Клиенты, которым будет отправлена рассылка.
    - owner (ForeignKey): Владелец рассылки, связанный с моделью пользователя (Users). Может быть пустым.
    """
    DAILY = 'D'
    WEEKLY = 'W'
    MONTHLY = 'M'
    PERIODICITY_CHOICES = [
        (DAILY, 'Ежедневно'),
        (WEEKLY, 'Еженедельно'),
        (MONTHLY, 'Ежемесячно'),
    ]

    CREATED = 'CREATED'
    STARTED = 'STARTED'
    COMPLETED = 'COMPLETED'
    STOPPED = 'STOPPED'
    STATUS_CHOICES = [
        (CREATED, 'Созданный'),
        (STARTED, 'Начатый'),
        (COMPLETED, 'Завершенный'),
        (STOPPED, 'Остановленный'),
    ]

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True, verbose_name="Дата и время окончания рассылки")
    periodicity = models.CharField(max_length=1, choices=PERIODICITY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=CREATED)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Client)
    owner = models.ForeignKey(Users, verbose_name='Собственник рассылки', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        permissions = [
            ("watch_mailings", "Может просматривать любые рассылки"),
            ("deactivate_mailings", "Может отключать рассылки"),
        ]

    def __str__(self):
        return f"{self.message.subject} - {self.start_datetime}"


class MailingAttempt(models.Model):
    """
    Модель, представляющая попытку отправки рассылки.

    Атрибуты:
    - mailing (ForeignKey): Ссылка на рассылку, к которой относится попытка.
    - attempt_datetime (DateTimeField): Дата и время попытки отправки (устанавливается автоматически).
    - status (CharField): Статус попытки (успешно или неудачно).
    - server_response (TextField): Ответ сервера. Может быть пустым.
    """
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
