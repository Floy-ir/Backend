import logging
from . import interfaces
from utils.date_time import interfaces as date_time_interfaces
from apps.airlines import interfaces as airlines_interfaces
from .interfaces import FlightDTO, WebsiteDTO
from .models import Flight, Website

logger = logging.getLogger(__name__)


class FlightsService(interfaces.AbstractFlightsService):
    def __init__(self,
                 date_time_utils: date_time_interfaces.AbstractDateTime,
                 airlines_service: airlines_interfaces.AbstractAirlineService
                 ):
        self.date_time = date_time_utils
        self.airlines_service = airlines_service


    def get_flights(self, request: interfaces.GetFlightsRequest) -> interfaces.GetFlightsResponse:
        logger.info(f"request: {request}")
        websites_field = ["price__lte", "price__gte", "remaining_seats__gte"]

        flight_filter = {}
        website_filter = {}
        website_uids = request.website_uids or []

        for key, value in request.as_dict():
            if key in websites_field:
                website_filter[f"websites__{key}"] = value
            else:
                flight_filter[key] = value

        flights_qs = Flight.objects.filter_flights_by_sites(
            website_uids=website_uids,
            flight_filters=flight_filter,
            website_filters=website_filter,
        )

        # TODO: get airline and website detail from cache
        result = interfaces.GetFlightsResponse(
            count=flights_qs.count(),
            results=[self._convert_flight_to_dto(flight) for flight in flights_qs]
        )
        logger.info("result: ", result)
        return result


    def create_flight(self, request: interfaces.CreateFlightRequest):
        pass


    def _convert_flight_to_dto(self, flight: Flight) -> FlightDTO:
        return interfaces.FlightDTO(
            airline=flight.airline,
            origin=flight.origin,
            destination=flight.destination,
            departure_timestamp=flight.departure_timestamp,
            arrival_timestamp=flight.arrival_timestamp,
            allowed_weight=flight.allowed_weight,
            seat_class=flight.seat_class,
            websites=[self._convert_website_to_dto(website) for website in flight.websites.all()],
        )

    @staticmethod
    def _convert_website_to_dto(website: Website) -> WebsiteDTO:
        return interfaces.WebsiteDTO(
            uid=website.uid,
            price=website.price,
            redirect_url=website.redirect_url,
            remaining_seat=website.remaining_seat,
        )
