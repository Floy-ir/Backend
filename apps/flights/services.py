import logging
from . import interfaces
from uuid import uuid4
from typing import List
from utils.date_time import interfaces as date_time_interfaces
from apps.airlines import interfaces as airlines_interfaces
from apps.accounts import interfaces as accounts_interfaces
from apps.flight_crawler import interfaces as flight_crawler_interfaces
from libs.redis_client import interfaces as cache_interfaces
from .models import Flight, Website
from constants import SECOND_IN_A_DAY

logger = logging.getLogger(__name__)


class FlightsService(interfaces.AbstractFlightsService):
    def __init__(self,
                 claim: accounts_interfaces.Session,
                 date_time_utils: date_time_interfaces.AbstractDateTime,
                 airlines_service: airlines_interfaces.AbstractAirlineService,
                 flight_crawler_service: flight_crawler_interfaces.AbstractFlightCrawler,
                 cache_service: cache_interfaces.ICacheService
                 ):
        self.claim = claim
        self.airline_details = None
        self.date_time = date_time_utils
        self.airlines_service = airlines_service
        self.cache_service = cache_service
        self.flight_crawler_service = flight_crawler_service

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

        website_filter["websites__is_valid"] = True

        flights_qs = Flight.objects.filter_flights_by_sites(
            website_uids=website_uids,
            flight_filters=flight_filter,
            website_filters=website_filter,
        )

        websites_uid = set()
        airlines_uid = set()
        allowed_weights = set()
        seat_classes = set()
        max_price = float('inf')
        airlines_min_price = {}
        websites_min_price = {}
        min_price = 0

        for flight in flights_qs:
            allowed_weights.add(flight.allowed_weight)
            seat_classes.add(flight.seat_classes)

            for website in flight.websites.all():
                websites_uid.add(website.uid)
                if websites_min_price.get(website.uid) is None:
                    websites_min_price[website.uid] = float('inf')

                min_price = min(min_price, website.price)
                max_price = max(max_price, website.price)
                websites_min_price[website.uid] = min(websites_min_price[website.uid], flight.price)

            airlines_uid.add(flight.airline)
            if flight.cheapest_price is not None:
                if airlines_min_price.get(flight.airline) is None:
                    airlines_min_price[flight.airline] = float('inf')

                airlines_min_price[flight.airline] = min(airlines_min_price[flight.airline], flight.cheapest_price)

        self.airline_details = self.airlines_service.get_airlines(
            request=airlines_interfaces.AirlineListReq(
                uid_list=list(airlines_uid)
            )
        )

        self.website_details = self.flight_crawler_service.get_websites(
            request=flight_crawler_interfaces.GetWebsitesRequest(
                uid_list=list(website_uids)
            )
        )

        airlines_filters = []
        for airline_uid, min_price in airlines_min_price.items():
            airlines_filters.append(
                interfaces.AirlineFilters(
                    uid=airline_uid,
                    min_price=min_price,
                    name=self.airline_details[airline_uid].name,
                    image=self.airline_details[airline_uid].image,
                )
            )


        websites_filters = []
        for website_uid, min_price in websites_min_price.items():
            websites_filters.append(
                interfaces.WebsiteFilters(
                    uid=website_uid,
                    name=self.website_details[website_uid].name,
                    name_fa=self.website_details[website_uid].name_fa,
                    image=self.website_details[website_uid].logo,
                    min_price=min_price,
                )
            )
            

        result = interfaces.GetFlightsResponse(
            count=flights_qs.count(),
            filters=interfaces.GetFlightsFilters(
                min_price=min_price,
                max_price=max_price,
                allowed_weights=list(allowed_weights),
                seat_classes=list(seat_classes),
                airlines=airlines_filters,
                #TODO: add websites filters
            ),
            results=[self._convert_flight_to_dto(flight) for flight in flights_qs]
        )
        logger.info("result: ", result)
        return result

    def get_cheapest_ticket(self, request: interfaces.GetCheapestTicketRequest) -> interfaces.GetCheapestResponse:
        logger.info(f"request: {request}")
        results: List[interfaces.FlightWithoutWebsiteDTO] = []
        base_timestamp = request.reference_timestamp

        for day_offset in range(request.forward_day):
            start_ts = base_timestamp + day_offset * SECOND_IN_A_DAY
            end_ts = start_ts + SECOND_IN_A_DAY
            cache_key = f"flights:cheapest:{start_ts}:{end_ts}"
            cheapest_flight = self.cache_service.get(cache_key)

            if cheapest_flight:
                results.append(self._convert_flight_dict_without_website_to_dto(cheapest_flight))
                continue

            cheapest_flight = (
                Flight.objects.filter(
                    origin=request.origin,
                    destination=request.destination,
                    departure_timestamp__gte=start_ts,
                    departure_timestamp__lt=end_ts,
                    cheapest_price__isnull=False
                )
                .order_by('cheapest_price')
                .first()
            )

            if cheapest_flight:
                cheapest_dto = self._convert_flight_db_without_website_to_dto(cheapest_flight)
                self.cache_service.set(cache_key, cheapest_dto)
                results.append(self._convert_flight_dict_without_website_to_dto(cheapest_flight))

        result = interfaces.GetCheapestResponse(
            count=len(results),
            results=results
        )
        logger.info("result: ", result)
        return result

    def create_flight(self, request: flight_crawler_interfaces.CrawlResponse):
        logger.info(f"Creating flight with request: {request}")
        
        created_flights = []
        for flight_data in request.results:
            flight, created = Flight.objects.get_or_create(
                airline=flight_data.airline,
                origin=flight_data.origin,
                destination=flight_data.destination,
                departure_timestamp=flight_data.departure_timestamp,
                arrival_timestamp=flight_data.arrival_timestamp,
                allowed_weight=flight_data.allowed_weight,
                seat_class=flight_data.seatClass,
                defaults={
                    "uid": str(uuid4())
                }
            )
            
            # Create the new website record
            Website.objects.create(
                uid=flight_data.provider_uid,
                flight=flight,
                adult_price=flight_data.adult_price,
                child_price=flight_data.child_price,
                infant_price=flight_data.infant_price,
                base_redirect_url=flight_data.redirect_url,
                one_adult_redirect_url=flight_data.one_adult_redirect_url,
                two_adult_redirect_url=flight_data.two_adult_redirect_url,
                remaining_seat=flight_data.remaining_seat,
                is_valid=True,
                last_crawled_uid=request.uid
            )
            
            flight.update_cheapest_info()
            logger.info(f"Created or updated flight with uid: {flight.uid}")
        

        Website.objects.filter(
            last_crawled_uid__ne=request.uid,
            flight__origin=request.origin,
            flight__destination=request.destination
        ).update(is_valid=False)
        logger.info(f"Processed {len(created_flights)} flights")

    def _convert_airline_to_dto(self, airline_uid: str) -> interfaces.Airline:
        airline_detail = self.airline_details[airline_uid]
        return interfaces.Airline(
            uid=airline_detail.uid,
            name=airline_detail.name,
            image=airline_detail.image
        )

    def _convert_flight_to_dto(self, flight: Flight) -> interfaces.FlightDTO:
        return interfaces.FlightDTO(
            airline=self._convert_airline_to_dto(flight.airline),
            origin=flight.origin,
            destination=flight.destination,
            departure_timestamp=flight.departure_timestamp,
            arrival_timestamp=flight.arrival_timestamp,
            allowed_weight=flight.allowed_weight,
            seat_class=flight.seat_class,
            websites=[self._convert_website_to_dto(website) for website in flight.websites.all()],
        )

    @staticmethod
    def _convert_flight_db_without_website_to_dto(flight: Flight) -> interfaces.FlightWithoutWebsiteDTO:
        return interfaces.FlightWithoutWebsiteDTO(
            airline=flight.airline,
            origin=flight.origin,
            destination=flight.destination,
            departure_timestamp=flight.departure_timestamp,
            arrival_timestamp=flight.arrival_timestamp,
            allowed_weight=flight.allowed_weight,
            seat_class=flight.seat_class,
            price=flight.cheapest_price,
            redirect_url=flight.cheapest_redirect_url,
            website_uid=flight.cheapest_website_uid,
        )

    @staticmethod
    def _convert_flight_dict_without_website_to_dto(flight: dict) -> interfaces.FlightWithoutWebsiteDTO:
        return interfaces.FlightWithoutWebsiteDTO(
            airline=flight["airline"],
            origin=flight["origin"],
            destination=flight["destination"],
            departure_timestamp=flight["departure_timestamp"],
            arrival_timestamp=flight["arrival_timestamp"],
            allowed_weight=flight["allowed_weight"],
            seat_class=flight["seat_class"],
            price=flight["cheapest_price"],
            redirect_url=flight["cheapest_redirect_url"],
            website_uid=flight["cheapest_website_uid"],
        )

    @staticmethod
    def _convert_website_to_dto(website: Website) -> interfaces.WebsiteDTO:
        return interfaces.WebsiteDTO(
            uid=website.uid,
            price=website.price,
            redirect_url=website.redirect_url,
            remaining_seat=website.remaining_seat,
        )
