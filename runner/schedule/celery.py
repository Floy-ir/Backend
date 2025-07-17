import os
from celery import Celery
import logging
from celery.schedules import crontab
from kombu import Connection

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'runner.settings')

BROKER_URL = os.getenv("BROKER_URL", "amqp://rabbitmq:5672")
THRESHOLD = 10       # Set your desired threshold

def get_queue_length(broker_url, queue_name):
    with Connection(broker_url) as conn:
        simple_queue = conn.SimpleQueue(queue_name)
        length = simple_queue.qsize()
        simple_queue.close()
        return length

class ThresholdCelery(Celery):
    def send_task(self, *args, **kwargs):
        if get_queue_length(BROKER_URL, QUEUE_NAME) < THRESHOLD:
            return super().send_task(*args, **kwargs)
        else:
            logger.warning("Queue is full, not adding new task: %s", args[0])
            return None

app = ThresholdCelery(
    'floy', 
    broker=BROKER_URL,
    config_source='runner.schedule.celery_config'
)

# Patch all tasks to check threshold before apply_async
from celery import Task as CeleryTask
_original_apply_async = CeleryTask.apply_async

def threshold_apply_async(self, *args, **kwargs):
    if get_queue_length(BROKER_URL, QUEUE_NAME) < THRESHOLD:
        return _original_apply_async(self, *args, **kwargs)
    else:
        logger.warning("Queue is full, not adding new task: %s", self.name)
        return None

CeleryTask.apply_async = threshold_apply_async

# Configure Celery settings
app.conf.update(
    beat_schedule_filename='/app/celerybeat-data/celerybeat-schedule',
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_pool_limit=10,
    worker_prefetch_multiplier=1,
    task_acks_late=False,
    task_acks_on_success=False,
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
