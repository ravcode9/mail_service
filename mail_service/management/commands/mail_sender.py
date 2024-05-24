from django.core.management.base import BaseCommand
from django.utils import timezone
from mail_service.models import Mailing, Log, Client, Message
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta

class Command(BaseCommand):
    help = 'Запускает службу рассылок'

    def handle(self, *args, **kwargs):
        self.send_mailing()

    def send_mailing(self):
        current_datetime = timezone.now()

        completed_mailings = Mailing.objects.filter(end_datetime__lt=current_datetime, status='started')
        for mailing in completed_mailings:
            mailing.status = 'completed'
            mailing.save()
            print(f"Рассылка {mailing.pk} завершена. Статус обновлён на 'завершена'.")

        print(f"Проверка рассылок для отправки на {current_datetime}")
        mailings = Mailing.objects.filter(
            start_datetime__lte=current_datetime,
            end_datetime__gte=current_datetime,
            status='started'
        )

        for mailing in mailings:
            if self.should_send_mailing(mailing, current_datetime):
                clients = mailing.clients.all()
                for client in clients:
                    try:
                        message = mailing.messages.first()
                        if message:
                            send_mail(
                                subject=message.subject,
                                message=message.body,
                                from_email=settings.EMAIL_HOST_USER,
                                recipient_list=[client.email]
                            )
                            Log.objects.create(
                                mailing=mailing,
                                datetime=current_datetime,
                                status=Log.STATUS_OK,
                                client=client,
                                server_response="Сообщение успешно доставлено"
                            )
                            print(f"Сообщение отправлено на {client.email} для рассылки {mailing.pk}")
                        else:
                            print(f"Сообщение не найдено для рассылки {mailing.pk}")
                    except Exception as e:
                        Log.objects.create(
                            mailing=mailing,
                            datetime=current_datetime,
                            status=Log.STATUS_FAILED,
                            client=client,
                            server_response=str(e)
                        )
                        print(f"Не удалось отправить сообщение на {client.email} для рассылки {mailing.pk}: {str(e)}")

    def should_send_mailing(self, mailing, current_datetime):
        last_log = Log.objects.filter(mailing=mailing, status=Log.STATUS_OK).order_by('-datetime').first()

        if last_log:
            if mailing.frequency == 'minutely':
                return current_datetime - last_log.datetime >= timedelta(minutes=1)
            elif mailing.frequency == 'daily':
                return current_datetime - last_log.datetime >= timedelta(days=1)
            elif mailing.frequency == 'weekly':
                return current_datetime - last_log.datetime >= timedelta(weeks=1)
            elif mailing.frequency == 'monthly':
                return current_datetime - last_log.datetime >= timedelta(days=30)
        else:
            return True
