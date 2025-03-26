from abc import ABC, abstractmethod
from .dataclasses import *
from typing import Dict


class AbstractFlightCrawler(ABC):
    @abstractmethod
    def crawl(self, request: CrawlRequest) -> CrawlResponse:
        raise NotImplementedError

    @abstractmethod
    def get_websites(self, request: GetWebsitesRequest) -> Dict[str, Website]:
        raise NotImplementedError

    @abstractmethod
    def upload_photo(self, request: UploadPhotoRequest) -> Website:
        raise NotImplementedError
