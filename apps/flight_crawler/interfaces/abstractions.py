from abc import ABC, abstractmethod
from .dataclasses import *
from typing import Dict, List, Optional


class AbstractFlightCrawler(ABC):
    @abstractmethod
    def crawl_scheduled_flights(
        self,
        from_days_ahead: int,
        to_days_ahead: int,
        routes: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """
            Crawl flights based on schedule parameters.
            
            Args:
                from_days_ahead: Inclusive lower bound for crawl window (0 for today)
                to_days_ahead: Exclusive upper bound for crawl window
                routes: Optional list of dicts with keys 'origin' and 'destination' to limit crawling
        """
        raise NotImplementedError

    @abstractmethod
    def get_websites(self, request: GetWebsitesRequest) -> Dict[str, WebsiteDTO]:
        raise NotImplementedError

    @abstractmethod
    def upload_image(self, request: UploadImageRequest) -> WebsiteDTO:
        raise NotImplementedError
