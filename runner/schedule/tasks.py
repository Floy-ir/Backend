from .celery import app
from runner.bootstrap import get_bootstrapper
from django.db import close_old_connections
import logging
import os
import json

logger = logging.getLogger(__name__)


@app.task
def crawl_three_days_ahead(): 
    # Close old database connections before starting the task
    close_old_connections()
    bootstrapper = None
    try:
        # Read routes from environment variable - check for instance-specific variables
        routes = None
        # Check for CRAWL_ROUTES_THREE_1 or CRAWL_ROUTES_THREE_2
        crawl_routes_env = os.getenv("CRAWL_ROUTES_THREE_1") or os.getenv("CRAWL_ROUTES_THREE_2") or ""
        if crawl_routes_env:
            try:
                routes = json.loads(crawl_routes_env)
                logger.info(f"Using {len(routes)} route(s) from CRAWL_ROUTES environment variable")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse CRAWL_ROUTES: {e}. Will crawl all routes.")
        
        bootstrapper = get_bootstrapper()
        service = bootstrapper.get_flight_crawler_service()
        service.crawl_scheduled_flights(from_days_ahead=0, to_days_ahead=5, routes=routes)
        logger.info("crawl_three_days_ahead completed successfully")
    except Exception as e:
        logger.error(f"Error in crawl_three_days_ahead: {e}")
        raise
    finally:
        if bootstrapper:
            bootstrapper.cleanup()

@app.task
def crawl_four_and_more_days_ahead(): 
    # Close old database connections before starting the task
    close_old_connections()
    bootstrapper = None
    try:
        bootstrapper = get_bootstrapper()
        service = bootstrapper.get_flight_crawler_service()
        service.crawl_scheduled_flights(from_days_ahead=5, to_days_ahead=14, routes=None)
        logger.info("crawl_four_and_more_days_ahead completed successfully")
    except Exception as e:
        logger.error(f"Error in crawl_four_and_more_days_ahead: {e}")
        raise
    finally:
        if bootstrapper:
            bootstrapper.cleanup()

@app.task()
def test_celery(): 
    # Close old database connections before starting the task
    close_old_connections()
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

