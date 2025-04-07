from runner.schedule.celery import Celery
from celery.schedules import crontab
from django.conf import settings
from apps.flight_crawler.models import WebsiteRoute

app = Celery('floy')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    'crawl-today-flights': {
        'task': 'apps.flight_crawler.tasks.crawl_flights',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'args': (1,),  # 1 day ahead
        'kwargs': {'priority_cities': True}
    },
    'crawl-tomorrow-flights': {
        'task': 'apps.flight_crawler.tasks.crawl_flights',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'args': (2,),  # 2 days ahead
        'kwargs': {'priority_cities': True}
    },
    'crawl-future-flights': {
        'task': 'apps.flight_crawler.tasks.crawl_flights',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'args': (None,),  # All future dates
        'kwargs': {'priority_cities': False}
    }
}
