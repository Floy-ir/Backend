import logging
from . import interfaces
from uuid import uuid4
from typing import List
from utils.date_time import interfaces as date_time_interfaces
from apps.airlines import interfaces as airlines_interfaces
from apps.accounts import interfaces as accounts_interfaces
from apps.event_bus import interfaces as event_bus_interfaces
from apps.flight_crawler import interfaces as flight_crawler_interfaces
from libs.redis_client import interfaces as cache_interfaces
from utils.date_time import interfaces as date_time_interfaces
from .models import Flight, Website
from constants import SECOND_IN_A_DAY
from django.db.models import Q

logger = logging.getLogger(__name__)


class FlightsService(interfaces.AbstractFlightsService, event_bus_interfaces.AbstractEventBus):
    def __init__(self,
                 claim: accounts_interfaces.Session,
                 event_bus: event_bus_interfaces.AbstractEventBus,
                 airlines_service: airlines_interfaces.AbstractAirlineService,
                 flight_crawler_service: flight_crawler_interfaces.AbstractFlightCrawler,
                 date_time_utils: date_time_interfaces.AbstractDateTime,
                 cache_service: cache_interfaces.ICacheService
                 ):
        self.claim = claim
        self.airline_details = None
        self.event_bus = event_bus
        self.airlines_service = airlines_service
        self.cache_service = cache_service
        self.flight_crawler_service = flight_crawler_service
        self.date_time_utils = date_time_utils  

        self.event_bus.subscribe(self.claim, 'flight_crawler_service/CRAWLED_FLIGHT', self)

    def on_event_or_command(self, emitter_claim: accounts_interfaces.Session,
                            event_or_command: event_bus_interfaces.EventOrCommand):
        if emitter_claim.user_uid == 'flight_crawler_service' and event_or_command.event_type == 'CRAWLED_FLIGHT':
            payload: flight_crawler_interfaces.CrawlResponse = event_or_command.payload
            self._create_flight(request=payload)

    def get_flights(self, request: interfaces.GetFlightsRequest) -> interfaces.GetFlightsResponse:
        logger.info(f"request: {request}")

        filter_field_map = {
            "airlines": "airline__in",
            "origin": "origin",
            "destination": "destination",
            "seat_classes": "seat_class__in",
            "allowed_weights": "allowed_weight__in",
            "departure_timestamp__gte": "departure_timestamp__gte",
            "departure_timestamp__lte": "departure_timestamp__lte",
            "arrival_timestamp__gte": "arrival_timestamp__gte",
            "arrival_timestamp__lte": "arrival_timestamp__lte",
            "websites": "websites__uid__in",
            "price__lte": "websites__price__lte",
            "price__gte": "websites__price__gte",
            "remaining_seats__gte": "websites__remaining_seat__gte",
        }

        flight_filter = {}
        website_filter = {}
        website_uids = request.websites or []

        for key, value in request.model_dump().items():
            if value is None: 
                continue
            
            mapped_key = filter_field_map.get(key)
            if mapped_key is None:
                continue
                
            if mapped_key.startswith('websites__'):
                website_filter[mapped_key] = value
            else:
                flight_filter[mapped_key] = value

        website_filter["websites__is_valid"] = True

        flights_qs = Flight.objects.filter_flights_by_sites(
            website_uids=website_uids,
            flight_filters=flight_filter,
            website_filters=website_filter,
        ).order_by('cheapest_price')

        if flights_qs.count() == 0:
            return interfaces.GetFlightsResponse(
                count=0,
                filters=interfaces.GetFlightsFilters(
                    min_price=0,
                    max_price=0,
                    allowed_weights=[],
                    seat_classes=[],
                    airlines=[],
                    websites=[],
                ),
                results=[],
            )

        websites_uid = set()
        airlines_uid = set()
        allowed_weights = set()
        seat_classes = set()
        max_price = float('-inf')
        min_price = float('inf')
        airlines_min_price = {}
        websites_min_price = {}

        for flight in flights_qs:
            allowed_weights.add(flight.allowed_weight)
            seat_classes.add(flight.seat_class)

            for website in flight.websites.all():
                websites_uid.add(website.uid)
                
                if websites_min_price.get(website.uid) is None:
                    websites_min_price[website.uid] = float('inf')

                min_price = min(min_price, website.adult_price)
                max_price = max(max_price, website.adult_price)
                websites_min_price[website.uid] = min(websites_min_price[website.uid], website.adult_price)

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
                uid_list=list(websites_uid)
            )
        )

        airlines_filters = []
        for airline_uid, min_price in airlines_min_price.items():
            airlines_filters.append(
                interfaces.AirlineFilters(
                    uid=airline_uid,
                    min_price=min_price,
                    name=self.airline_details[airline_uid].name,
                    logo=self.airline_details[airline_uid].image,
                )
            )


        websites_filters = []
        for website_uid, min_price in websites_min_price.items():
            websites_filters.append(
                interfaces.WebsiteFilters(
                    uid=website_uid,
                    name=self.website_details[website_uid].name,
                    name_fa=self.website_details[website_uid].name_fa,
                    logo=self.website_details[website_uid].logo,
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
                websites=websites_filters,
            ),
            results=[self._convert_flight_to_dto(flight) for flight in flights_qs]
        )
        logger.info(f"result: {result}")
        return result

    def get_cheapest_ticket(self, request: interfaces.GetCheapestTicketRequest) -> interfaces.GetCheapestResponse:
        logger.info(f"request: {request}")
        results: List[interfaces.CheapestFlightDTO] = []
        base_timestamp = self.date_time_utils.convert_datetime_string_to_timestamp(request.reference_date, '%Y-%m-%d')

        total_days = request.forward_day + request.backward_day
        start_day = -request.backward_day

        flights = Flight.objects.filter(
            origin=request.origin,
            destination=request.destination,
            departure_timestamp__gte=base_timestamp + (start_day * SECOND_IN_A_DAY),
            departure_timestamp__lt=base_timestamp + ((start_day + total_days) * SECOND_IN_A_DAY),
            cheapest_price__isnull=False
        ).order_by('departure_timestamp', 'cheapest_price')

        flights_by_day = {}
        for flight in flights:
            day_offset = (flight.departure_timestamp - base_timestamp) // SECOND_IN_A_DAY
            if day_offset not in flights_by_day:
                flights_by_day[day_offset] = []
            flights_by_day[day_offset].append(flight)

        for day_offset in range(start_day, request.forward_day):
            start_ts = base_timestamp + day_offset * SECOND_IN_A_DAY
            start_date = self.date_time_utils.convert_timestamp_to_date(start_ts, '%Y-%m-%d')
            # Get the cheapest flight for this day if any exists
            cheapest_flight = None
            if day_offset in flights_by_day and flights_by_day[day_offset]:
                cheapest_flight = flights_by_day[day_offset][0]

            if cheapest_flight:
                cheapest_dto = interfaces.CheapestFlightDTO(
                    origin=cheapest_flight.origin,
                    destination=cheapest_flight.destination,
                    date=start_date,
                    price=cheapest_flight.cheapest_price,
                )
            else:
                cheapest_dto = interfaces.CheapestFlightDTO(
                    origin=request.origin,
                    destination=request.destination,
                    date=start_date,
                    price=0,
                )
            results.append(cheapest_dto)

        result = interfaces.GetCheapestResponse(
            count=len(results),
            results=results
        )
        logger.info(f"result: {result}")
        return result

    def _create_flight(self, request: flight_crawler_interfaces.CrawlResponse):
        logger.info(f"Creating flight with request: {request}")
        
        for flight_data in request.results:
            flight, created = Flight.objects.get_or_create(
                airline=flight_data.airline,
                origin=request.origin,
                destination=request.destination,
                departure_timestamp=flight_data.departure_timestamp,
                arrival_timestamp=flight_data.arrival_timestamp,
                allowed_weight=flight_data.allowed_weight,
                seat_class=flight_data.seat_class,
                defaults={
                    "uid": str(uuid4())
                }
            )

            website, created = Website.objects.get_or_create(
                uid=flight_data.provider_uid,
                flight=flight,
                defaults={
                    "base_redirect_url": flight_data.base_redirect_url,
                    "one_adult_redirect_url": flight_data.one_adult_redirect_url,
                    "two_adult_redirect_url": flight_data.two_adult_redirect_url,
                    "adult_price": flight_data.adult_price,
                    "child_price": flight_data.child_price,
                    "infant_price": flight_data.infant_price,
                    "remaining_seat": flight_data.remaining_seat,
                    "last_crawled_uid": request.uid,
                }
            )
            
            if not created and website.last_crawled_uid == request.uid: 
                if flight_data.one_adult_redirect_url is not None: 
                    website.one_adult_redirect_url = flight_data.one_adult_redirect_url
                if flight_data.two_adult_redirect_url is not None:
                    website.two_adult_redirect_url = flight_data.two_adult_redirect_url
                if flight_data.base_redirect_url is not None:
                    website.base_redirect_url = flight_data.base_redirect_url
                
                if flight_data.adult_price is not None:
                    website.adult_price = flight_data.adult_price
                if flight_data.child_price is not None:
                    website.child_price = flight_data.child_price
                if flight_data.infant_price is not None:
                    website.infant_price = flight_data.infant_price
            
            elif not created and website.last_crawled_uid != request.uid:
                website.one_adult_redirect_url = flight_data.one_adult_redirect_url
                website.two_adult_redirect_url = flight_data.two_adult_redirect_url
                website.base_redirect_url = flight_data.base_redirect_url
                website.adult_price = flight_data.adult_price
                website.child_price = flight_data.child_price
                website.infant_price = flight_data.infant_price
                website.remaining_seat = flight_data.remaining_seat
                website.is_valid = True
                website.last_crawled_uid = request.uid

            remaining_seat = flight_data.remaining_seat if flight_data.remaining_seat is not None else 0
            if remaining_seat > 0:
                website.remaining_seat = remaining_seat
                website.is_valid = True
            else:
                website.is_valid = False
                
            website.last_crawled_uid = request.uid

            website.save()
                
            logger.debug(f"\n\nwebsite: {website.__dict__}\n\n")
            
            flight.update_cheapest_info()
            logger.info(f"Created or updated flight with uid: {flight.uid}")
        

        print(f"\n\nrequest.crawl_timestamp: {request.crawl_timestamp}\n\n")
        print(f"\n\nrequest.crawl_timestamp + SECOND_IN_A_DAY: {request.crawl_timestamp + SECOND_IN_A_DAY}\n\n")

        Website.objects.filter(
            ~Q(last_crawled_uid=request.uid),
            flight__origin=request.origin,
            flight__destination=request.destination,
            flight__departure_timestamp__gte=request.crawl_timestamp,
            flight__departure_timestamp__lt=request.crawl_timestamp + SECOND_IN_A_DAY
        ).update(is_valid=False)


    def _convert_flight_to_dto(self, flight: Flight) -> interfaces.FlightDTO:
        return interfaces.FlightDTO(
            airline=interfaces.AirlineDetail(
                uid=flight.airline,
                name=self.airline_details[flight.airline].name,
                logo=self.airline_details[flight.airline].image
            ),
            origin=flight.origin,
            destination=flight.destination,
            departure_timestamp=flight.departure_timestamp,
            arrival_timestamp=flight.arrival_timestamp,
            allowed_weight=flight.allowed_weight,
            seat_class=flight.seat_class,
            cheapest_price=flight.cheapest_price,
            cheapest_base_redirect_url=flight.cheapest_base_redirect_url,
            cheapest_one_adult_redirect_url=flight.cheapest_one_adult_redirect_url,
            cheapest_two_adult_redirect_url=flight.cheapest_two_adult_redirect_url,
            cheapest_website=interfaces.WebsiteDetail(
                uid=flight.cheapest_website_uid,
                name=self.website_details[flight.cheapest_website_uid].name,
                name_fa=self.website_details[flight.cheapest_website_uid].name_fa,
                logo=self.website_details[flight.cheapest_website_uid].logo
            ),
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
            redirect_url=flight.cheapest_base_redirect_url,
            website=flight.cheapest_website_uid,
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
            redirect_url=flight["cheapest_base_redirect_url"],
            website=flight["cheapest_website"],
        )

    def _convert_website_to_dto(self, website: Website) -> interfaces.WebsiteDTO:
        return interfaces.WebsiteDTO(
            detail=interfaces.WebsiteDetail(
                uid=website.uid,
                name=self.website_details[website.uid].name,
                name_fa=self.website_details[website.uid].name_fa,
                logo=self.website_details[website.uid].logo,
            ),
            adult_price=website.adult_price,
            child_price=website.child_price,
            infant_price=website.infant_price,
            base_redirect_url=website.base_redirect_url,
            one_adult_redirect_url=website.one_adult_redirect_url,
            two_adult_redirect_url=website.two_adult_redirect_url,
            remaining_seat=website.remaining_seat,
        )
