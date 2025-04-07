from abc import ABC, abstractmethod
from .dataclasses import *
from typing import Dict


class AbstractFlightCrawler(ABC):
    @abstractmethod
    def crawl_scheduled_flights(self, days_ahead: int = None) -> None:         
        """
            Crawl flights based on schedule parameters.
            
            Args:
                days_ahead: Number of days ahead to crawl (None for all future dates)
                priority_cities: Whether to only crawl priority city routes
        """
        raise NotImplementedError

    @abstractmethod
    def crawl(self, request: CrawlRequest) -> CrawlResponse:
        raise NotImplementedError

    @abstractmethod
    def get_websites(self, request: GetWebsitesRequest) -> Dict[str, WebsiteDTO]:
        raise NotImplementedError

    @abstractmethod
    def upload_image(self, request: UploadImageRequest) -> WebsiteDTO:
        raise NotImplementedError
