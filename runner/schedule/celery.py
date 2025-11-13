import os
from typing import List, Dict
from celery import Celery
import logging
from celery.schedules import crontab
from kombu import Connection

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'runner.settings')

BROKER_URL = os.getenv("BROKER_URL", "amqp://rabbitmq:5672")
QUEUE_NAME = "celery"  # Change if you use a custom queue
THRESHOLD = 10       # Set your desired threshold
BEAT_ROLE = os.getenv("BEAT_ROLE", "both")
BEAT_SCHEDULE_FILE = os.getenv("BEAT_SCHEDULE_FILE", "/app/celerybeat-data/celerybeat-schedule")

def _get_int_env(name: str, default: int, minimum: int = 0, maximum: int = 60) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        value = int(raw_value)
    except ValueError:
        logger.warning("Invalid integer for %s: %s. Using default %s.", name, raw_value, default)
        return default

    if minimum is not None and value < minimum:
        logger.warning("%s must be >= %s. Using default %s.", name, minimum, default)
        return default

    if maximum is not None and value > maximum:
        logger.warning("%s must be <= %s. Using default %s.", name, maximum, default)
        return default

    return value


def _parse_routes(raw_routes: str) -> List[Dict[str, str]]:
    routes: List[Dict[str, str]] = []
    if not raw_routes:
        return routes

    for item in raw_routes.split(","):
        candidate = item.strip()
        if not candidate:
            continue

        try:
            origin, destination = candidate.split(":", 1)
        except ValueError:
            logger.warning("Invalid route specification '%s'. Expected format ORG:DST.", candidate)
            continue

        origin = origin.strip().upper()
        destination = destination.strip().upper()

        if not origin or not destination:
            logger.warning("Empty origin or destination in route specification '%s'. Skipping.", candidate)
            continue

        routes.append({"origin": origin, "destination": destination})

    return routes


def _build_minute_expression(offset: int, interval: int) -> str:
    offset = offset % 60
    if interval >= 60:
        return str(offset)
    return f"{offset}-59/{max(interval, 1)}"


THREE_DAY_INTERVAL_MINUTES = _get_int_env("THREE_DAY_INTERVAL_MINUTES", default=10, minimum=1)
FOUR_PLUS_INTERVAL_MINUTES = _get_int_env("FOUR_PLUS_INTERVAL_MINUTES", default=20, minimum=1)
THREE_DAY_OFFSET_MINUTE = _get_int_env("THREE_DAY_OFFSET_MINUTE", default=0, minimum=0, maximum=59)
FOUR_PLUS_OFFSET_MINUTE = _get_int_env("FOUR_PLUS_OFFSET_MINUTE", default=5, minimum=0, maximum=59)
CRAWL_ROUTES = _parse_routes(os.getenv("CRAWL_ROUTES", ""))

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
    beat_schedule_filename=BEAT_SCHEDULE_FILE,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_pool_limit=10,
    worker_prefetch_multiplier=1,
    task_acks_late=False,
    task_acks_on_success=False,
    # Memory management settings
    worker_max_memory_per_child=512000,  # 512MB per worker
    worker_max_tasks_per_child=100,     # Restart worker after 100 tasks
    worker_disable_rate_limits=True,
    task_ignore_result=True,             # Don't store task results
    result_expires=3600,                # Expire results after 1 hour
    # Connection management
    broker_connection_retry=True,
    broker_heartbeat=30,
    # Task execution settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Configure Celery Beat schedule based on BEAT_ROLE
role = (BEAT_ROLE or "").lower()
schedule_entries = {}

if role in ("three_days", "both", ""):
    three_day_entry = {
        'task': 'runner.schedule.tasks.crawl_three_days_ahead',
        'schedule': crontab(minute=_build_minute_expression(
            THREE_DAY_OFFSET_MINUTE,
            THREE_DAY_INTERVAL_MINUTES,
        )),
    }

    if CRAWL_ROUTES:
        three_day_entry['kwargs'] = {'routes': CRAWL_ROUTES}

    schedule_entries['crawl_three_days_ahead'] = three_day_entry

if role in ("four_plus", "both", ""):
    four_plus_entry = {
        'task': 'runner.schedule.tasks.crawl_four_and_more_days_ahead',
        'schedule': crontab(minute=_build_minute_expression(
            FOUR_PLUS_OFFSET_MINUTE,
            FOUR_PLUS_INTERVAL_MINUTES,
        )),
    }

    if CRAWL_ROUTES:
        four_plus_entry['kwargs'] = {'routes': CRAWL_ROUTES}

    schedule_entries['crawl_four_and_more_days_ahead'] = four_plus_entry

app.conf.beat_schedule = schedule_entries
