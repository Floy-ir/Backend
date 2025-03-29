from abc import ABC, abstractmethod
from .dataclasses import *
from typing import Dict


class AbstractFlightCrawler(ABC):
    @abstractmethod
    def crawl(self, request: CrawlRequest) -> CrawlResponse:
        raise NotImplementedError

    @abstractmethod
    def get_websites(self, request: GetWebsitesRequest) -> Dict[str, WebsiteDTO]:
        raise NotImplementedError

    @abstractmethod
    def upload_image(self, request: UploadImageRequest) -> WebsiteDTO:
        raise NotImplementedError
