from .dataclasses import *
from abc import ABC, abstractmethod


class AbstractAirlineService(ABC):
    @abstractmethod
    def get_airline(self, uid: str) -> Airline:
        """
        this
        """
        raise NotImplementedError

    @abstractmethod
    def get_airlines(self, request: AirlineListReq) -> Airlines:
        """
        this method will give service to flight service when want to return airline of flight.
        """
        raise NotImplementedError

