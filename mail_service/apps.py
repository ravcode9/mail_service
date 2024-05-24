import os
import logging
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
from django.apps import AppConfig

scheduler_started = False
scheduler_lock = threading.Lock()
logger = logging.getLogger(__name__)


def sending_mail():
    call_command('mail_sender')


def start_scheduler():
    global scheduler_started
    with scheduler_lock:
        if not scheduler_started and os.environ.get('RUN_MAIN', None) != 'true':
            scheduler = BackgroundScheduler()
            scheduler.add_job(sending_mail, 'interval', seconds=5)
            scheduler.start()
            scheduler_started = True
            logger.info("Служба рассылок запущена. Ожидание запланированных задач...")
        else:
            logger.info("Планировщик уже запущен или работает в основном потоке.")


class MailServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mail_service'
    verbose_name = 'Рассылки'

    def ready(self):
        start_scheduler()
