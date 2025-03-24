from .dataclasses import *
from abc import ABC, abstractmethod
from typing import Dict


class AbstractAirlineService(ABC):
    @abstractmethod
    def get_airline(self, uid: str) -> AirlineDTO:
        """
        """
        raise NotImplementedError

    @abstractmethod
    def upload_image(self, request: UploadImageReq) -> AirlineDTO:
        """
        this method is for upload image for every airline.
        """
        raise NotImplementedError

    @abstractmethod
    def get_airlines(self, request: AirlineListReq) -> Dict[str, AirlineDTO]:
        """
        this method will give service to flight service when want to return airline of flight.
        """
        raise NotImplementedError


    @abstractmethod
    def get_airline_by_name(self, name: str) -> AirlineDTO:
        """
        this method is used to get airline by name and if it doesn't exist it create a new one.
        """
        raise NotImplementedError


