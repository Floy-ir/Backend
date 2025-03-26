from .dataclasses import *
from abc import ABC, abstractmethod
from typing import Dict


class AbstractAirlineService(ABC):
    @abstractmethod
    def get_airline(self, uid: str) -> AirlineDTO:
        """
        Get airline data by UID from cache first, if not found, query the database.
        """
        raise NotImplementedError

    @abstractmethod
    def upload_image(self, request: UploadImageReq) -> AirlineDTO:
        """
        Upload image for a specific airline, cache the updated airline.
        """
        raise NotImplementedError

    @abstractmethod
    def get_airlines(self, request: AirlineListReq) -> Dict[str, AirlineDTO]:
        """
        Get multiple airlines by a list of UIDs, checking cache first.
        """
        raise NotImplementedError


    @abstractmethod
    def get_airline_by_name(self, name: str) -> AirlineDTO:
        """
        Get an airline by its name, checking cache first. If not found, create new airline.
        """
        raise NotImplementedError


