from . import interfaces
from utils.date_time import interfaces as date_time_interfaces
from .interfaces import CreateFlightRequest


class FlightsService(interfaces.AbstractFlightsService):
    def __init__(self, date_time_utils: date_time_interfaces.AbstractDateTime):
        self.date_time = date_time_utils


    def get_flights(self, request: interfaces.GetFlightsRequest) -> interfaces.GetFlightsResponse:


    def create_flight(self, request: CreateFlightRequest):
        pass
