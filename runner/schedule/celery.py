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

# Configure Celery settings
app.conf.update(
    beat_schedule_filename='/app/celerybeat-data/celerybeat-schedule',
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_pool_limit=10,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    'crawl_three_days_ahead': {
        'task': 'runner.schedule.tasks.crawl_three_days_ahead',
        'schedule': crontab(minute='0-59/10'),  # 0, 10, 20, 30, ...
    },
    'crawl_four_and_more_days_ahead': {
        'task': 'runner.schedule.tasks.crawl_four_and_more_days_ahead',
        'schedule': crontab(minute='5-59/10'),  # 5, 15, 25, 35, ...
    },
}
