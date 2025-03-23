from abc import ABC, abstractmethod
from .dataclasses import *

class AbstractFlightsService(ABC):
    @abstractmethod
    def get_flights(self, request: GetFlightsRequest) -> GetFlightsResponse:
        raise NotImplementedError

    @abstractmethod
    def get_cheapest_ticket(self, request: GetCheapestTicketRequest) -> GetCheapestResponse:
        raise NotImplementedError

    @abstractmethod
    def create_flight(self, request: CreateFlightRequest):
        raise NotImplementedError