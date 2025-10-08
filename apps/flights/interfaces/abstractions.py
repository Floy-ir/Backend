from abc import ABC, abstractmethod
from .dataclasses import *
from apps.flight_crawler import interfaces as flight_crawler_interfaces

class AbstractFlightsService(ABC):
    @abstractmethod
    def get_flights(self, request: GetFlightsRequest) -> GetFlightsResponse:
        raise NotImplementedError

    @abstractmethod
    def get_cheapest_ticket(self, request: GetCheapestTicketRequest) -> GetCheapestResponse:
        raise NotImplementedError

    @abstractmethod
    def create_flight(self, request: flight_crawler_interfaces.CrawlResponse) -> None:
        raise NotImplementedError
