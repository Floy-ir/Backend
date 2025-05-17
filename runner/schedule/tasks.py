from .celery import app
from runner.bootstrap import get_bootstrapper


@app.task
def crawl_three_days_ahead(): 
    service = get_bootstrapper().get_flight_crawler_service()
    service.crawl_scheduled_flights(from_days_ahead=0, to_days_ahead=5)

@app.task
def crawl_four_and_more_days_ahead(): 
    service = get_bootstrapper().get_flight_crawler_service()
    service.crawl_scheduled_flights(from_days_ahead=5, to_days_ahead=14)

@app.task()
def test_celery(): 
    service = get_bootstrapper().get_flight_crawler_service()
    service.test_celery()