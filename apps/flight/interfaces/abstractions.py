from abc import ABC, abstractmethod
from .dataclasses import *

class AbstractFlightService(ABC):
    @abstractmethod
    def get_flights(self, request: GetFlightsRequest) -> GetFlightsResponse:
        raise NotImplementedError

    @abstractmethod
    def create_flights(self, request: CreateFlightRequest):
        raise NotImplementedError
