from celery import shared_task
import logging
from typing import Optional
from runner.bootstrap import get_bootstrapper

logger = logging.getLogger(__name__)

@shared_task
def crawl_flights(days_ahead: Optional[int] = None, priority_cities: bool = False):
    """
    Celery task to crawl flights based on the specified parameters.
    
    Args:
        days_ahead: Number of days ahead to crawl (None for all future dates)
        priority_cities: Whether to only crawl priority city routes
    """
    try:
        service = get_bootstrapper().get_flight_crawler_service()
        service.crawl_scheduled_flights(days_ahead=days_ahead, priority_cities=priority_cities)
    except Exception as e:
        logger.error(f"Error in crawl_flights task: {str(e)}")
        raise 