import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'runner.settings')

app = Celery('backend',
             broker=os.getenv("BROKER_URL", "amqp://rabbitmq:5672"),
             config_source='runner.schedule.celery_config')

app.conf.beat_schedule = {
    'tour_robot': {
        'task': 'runner.schedule.tasks.tour_robot',
        'schedule': crontab(hour=5, minute=0),  # Run at 5:00 AM every day
    },
}
