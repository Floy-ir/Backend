import os
from celery import Celery
import logging
from celery.schedules import crontab


logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'runner.settings')

app = Celery(
    'floy', 
    broker=os.getenv("BROKER_URL", "amqp://rabbitmq:5672"),
    config_source='runner.schedule.celery_config'
    )


# Configure Celery Beat schedule
app.conf.beat_schedule = {
    'crawl_three_days_ahead': {
        'task': 'runner.schedule.tasks.crawl_three_days_ahead',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'kwargs': {'priority_cities': True}
    },
    'crawl_four_and_more_days_ahead': {
        'task': 'runner.schedule.tasks.crawl_four_and_more_days_ahead',
        'schedule': crontab(minute='*/10'),  # Every 15 minutes
        'kwargs': {'priority_cities': False}
    },
    'test_celery': {
        'task': 'runner.schedule.tasks.test_celery',
        'schedule': crontab(minute='*/1'), 
    }
}
