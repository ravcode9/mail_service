from django.conf import settings
from django.db import models


class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=100, verbose_name='Ф. И. О.', blank=True, null=True)
    comment = models.TextField(verbose_name='Комментарий', blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='owner_client',
                              verbose_name="владелец", blank=True, null=True)

    def __str__(self):
        return f'{self.email} - {self.full_name}'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Mailing(models.Model):
    start_datetime = models.DateTimeField(verbose_name='Дата и время начала')
    end_datetime = models.DateTimeField(verbose_name='Дата и время окончания')
    frequency_choices = [
        ('minutely', 'Ежеминутно'),
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
        ('monthly', 'Ежемесячно'),
    ]
    frequency = models.CharField(max_length=20, choices=frequency_choices, verbose_name='Периодичность')
    status_choices = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена')
    ]
    status = models.CharField(max_length=10, choices=status_choices, verbose_name='Статус')
    clients = models.ManyToManyField(Client, verbose_name='Клиенты')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='owner',
                              verbose_name="владелец", blank=True, null=True)

    def __str__(self):
        return f'Mailing - {self.pk}'

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

        permissions = [
            (
                'change_status',
                'Can change status'
            )
        ]


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')
    mailing_list = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name='Рассылка',
                                     related_name='messages')

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Log(models.Model):
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name='Рассылка')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время')
    STATUS_OK = 'OK'
    STATUS_FAILED = 'failed'
    STATUSES = (
        (STATUS_OK, 'Успешно'),
        (STATUS_FAILED, 'Ошибка'),
    )

    status = models.CharField(default=STATUS_OK, max_length=20, choices=STATUSES, verbose_name="Статус")
    server_response = models.TextField(verbose_name='Ответ сервера', blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='клиент рассылки', null=True)

    def __str__(self):
        return f'Log - {self.pk}'

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылки'
