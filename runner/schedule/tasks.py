from .celery import app
from runner.bootstrap import get_bootstrapper
import logging

logger = logging.getLogger(__name__)


@app.task
def crawl_three_days_ahead(): 
    bootstrapper = None
    try:
        bootstrapper = get_bootstrapper()
        service = bootstrapper.get_flight_crawler_service()
        service.crawl_scheduled_flights(from_days_ahead=0, to_days_ahead=5)
        logger.info("crawl_three_days_ahead completed successfully")
    except Exception as e:
        logger.error(f"Error in crawl_three_days_ahead: {e}")
        raise
    finally:
        if bootstrapper:
            bootstrapper.cleanup()

@app.task
def crawl_four_and_more_days_ahead(): 
    bootstrapper = None
    try:
        bootstrapper = get_bootstrapper()
        service = bootstrapper.get_flight_crawler_service()
        service.crawl_scheduled_flights(from_days_ahead=0, to_days_ahead=14)
        logger.info("crawl_four_and_more_days_ahead completed successfully")
    except Exception as e:
        logger.error(f"Error in crawl_four_and_more_days_ahead: {e}")
        raise
    finally:
        if bootstrapper:
            bootstrapper.cleanup()

@app.task()
def test_celery(): 
    bootstrapper = None
    try:
        bootstrapper = get_bootstrapper()
        service = bootstrapper.get_flight_crawler_service()
        service.test_celery()
        logger.info("test_celery completed successfully")
    except Exception as e:
        logger.error(f"Error in test_celery: {e}")
        raise
    finally:
        if bootstrapper:
            bootstrapper.cleanup()

