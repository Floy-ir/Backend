import abc
from apps.accounts import interfaces as accounts_interfaces
from .dataclasses import *


class AbstractFlightCityService(abc.ABC):
    def create_city(self, request: CreateCityRequest):
        """
        creating city
        """
        raise NotImplementedError


    def add_destination(self, request: AddDestinationRequest):
        """
        add new path to an existence city
        """
        raise NotImplementedError


    def get_cities(self, request: GetCitiesRequest) -> CityList:
        """
        this will be export by an API.

        Return:
            - CityList: list of all cities and for each of them allowed city
        """
        raise NotImplementedError


    def get_city(self, request: GetCityRequest) -> GetCityResponse:
        """
        this method is just called by other services to get detail of one city

        Return:
            - GetCityResponse: detail of a specific city
        """
        raise NotImplementedError
