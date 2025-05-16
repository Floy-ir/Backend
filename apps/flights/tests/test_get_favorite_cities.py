from uuid import uuid4
from django.test import TestCase
from apps.accounts import interfaces as accounts_interfaces
from apps.event_bus import interfaces as event_bus_interfaces
from apps.flight_crawler import interfaces as flight_crawler_interfaces
from .fake_modules import *
from .. import interfaces
from runner.bootstrap import get_bootstrapper
from constants import SECOND_IN_A_DAY
from datetime import datetime

class EventCommandTestCase(TestCase): 
    def setUp(self) -> None:

        self.alibaba = "alibaba"
        self.flightio = "flightio"
        self.pate = "pate"
        
        bootstrapper = get_bootstrapper(
            airlines_service=FakeAirlineService(),
            cache_service=FakeCacheService(),
            flight_crawler_service=FakeFlightCrawlerService(),
            event_bus=FakeEventBus(),
        )

        self.service = bootstrapper.get_flights_service()

        self.current_timestamp = int(datetime.now().timestamp())

        print(f"\n\ncurrent_timestamp ==>> {self.current_timestamp}\n\n")
        
        self.service.on_event_or_command(
            emitter_claim=accounts_interfaces.Session.for_internal_app(uid='flight_crawler_service'),
            event_or_command=event_bus_interfaces.EventOrCommand(
                uid=str(uuid4()),
                event_type='CRAWLED_FLIGHT',
                payload=flight_crawler_interfaces.CrawlResponse(
                    uid=str(uuid4()),
                    crawl_timestamp=current_timestamp,
                    origin='THR',
                    destination='MHD',
                    results=[
                        flight_crawler_interfaces.Flight(
                            airline='kish',
                            flight_number='10',
                            departure_timestamp=self.current_timestamp + 18,
                            arrival_timestamp=self.current_timestamp + 24,
                            seat_class='Economy',
                            allowed_weight=20,
                            adult_price=1000,
                            child_price=None,
                            infant_price=None,
                            airplane_name=None,
                            remaining_seat=3,
                            provider_uid=self.alibaba,
                            one_adult_redirect_url="alibaba.ir/one_adult_redirect_url",
                            two_adult_redirect_url=None,
                            base_redirect_url="alibaba.ir"
                        ),
                        flight_crawler_interfaces.Flight(
                            airline='kish',
                            flight_number='10',
                            departure_timestamp=self.current_timestamp + 13,
                            arrival_timestamp=self.current_timestamp + 24,
                            seat_class='Economy',
                            allowed_weight=20,
                            adult_price=1000,
                            child_price=500,
                            infant_price=200,
                            airplane_name=None,
                            remaining_seat=3,
                            provider_uid=self.alibaba,
                            one_adult_redirect_url=None,
                            two_adult_redirect_url="alibaba.ir/two_adult_redirect_url",
                            base_redirect_url="alibaba.ir"
                        ),
                        flight_crawler_interfaces.Flight(
                            airline='kish',
                            flight_number='10',
                            departure_timestamp=self.current_timestamp + 13,
                            arrival_timestamp=self.current_timestamp + 24,
                            seat_class='Economy',
                            allowed_weight=20,
                            adult_price=1100,
                            child_price=600,
                            infant_price=100,
                            airplane_name=None,
                            remaining_seat=2,
                            provider_uid=self.flightio,
                            one_adult_redirect_url="flightio.com/one_adult_redirect_url",
                            two_adult_redirect_url=None,
                            base_redirect_url="flightio.com"
                        ),
                        flight_crawler_interfaces.Flight(
                            airline='kish',
                            flight_number='10',
                            departure_timestamp=self.current_timestamp + 13,
                            arrival_timestamp=self.current_timestamp + 24,
                            seat_class='Economy',
                            allowed_weight=20,
                            adult_price=1100,
                            child_price=600,
                            infant_price=100,
                            airplane_name=None,
                            remaining_seat=2,
                            provider_uid=self.flightio,
                            one_adult_redirect_url=None,
                            two_adult_redirect_url="flightio.com/two_adult_redirect_url",
                            base_redirect_url="flightio.com"
                        ),
                        flight_crawler_interfaces.Flight(
                            airline='qeshm',
                            flight_number='11',
                            departure_timestamp=self.current_timestamp + 16,
                            arrival_timestamp=self.current_timestamp + 18,
                            seat_class='Economy',
                            allowed_weight=25,
                            adult_price=1100,
                            child_price=500,
                            infant_price=200,
                            airplane_name=None,
                            remaining_seat=1,
                            provider_uid=self.flightio,
                            one_adult_redirect_url="flightio.com/one_adult_redirect_url",
                            two_adult_redirect_url=None,
                            base_redirect_url="flightio.com"
                        ),
                        flight_crawler_interfaces.Flight(
                            airline='qeshm',
                            flight_number='11',
                            departure_timestamp=self.current_timestamp + 16,
                            arrival_timestamp=self.current_timestamp + 18,
                            seat_class='Economy',
                            allowed_weight=25,
                            adult_price=1300,
                            child_price=700,
                            infant_price=300,
                            airplane_name=None,
                            remaining_seat=1,
                            provider_uid=self.pate,
                            one_adult_redirect_url=None,
                            two_adult_redirect_url="pateh.com/two_adult_redirect_url",
                            base_redirect_url="pateh.com"
                        ),
                        flight_crawler_interfaces.Flight(
                            airline='Iranair',
                            flight_number='12',
                            departure_timestamp=self.current_timestamp + 19,
                            arrival_timestamp=self.current_timestamp + 21,
                            seat_class='Economy',
                            allowed_weight=30,
                            adult_price=1500,
                            child_price=800,
                            infant_price=400,
                            airplane_name=None,
                            remaining_seat=2,
                            provider_uid=self.pate,
                            one_adult_redirect_url=None,
                            two_adult_redirect_url=None,
                            base_redirect_url="pate.com"
                        ),
                    ]

                )
            )
        )

        self.service.on_event_or_command(
            emitter_claim=accounts_interfaces.Session.for_internal_app(uid='flight_crawler_service'),
            event_or_command=event_bus_interfaces.EventOrCommand(
                uid=str(uuid4()),
                event_type='CRAWLED_FLIGHT',
                payload=flight_crawler_interfaces.CrawlResponse(
                    uid=str(uuid4()),
                    crawl_timestamp=current_timestamp,
                    origin='THR',
                    destination='KIH',
                    results=[
                        flight_crawler_interfaces.Flight(
                            airline='kish',
                            flight_number='10',
                            departure_timestamp=self.current_timestamp + 13,
                            arrival_timestamp=self.current_timestamp + 24,
                            seat_class='Economy',
                            allowed_weight=20,
                            adult_price=400,
                            child_price=None,
                            infant_price=None,
                            airplane_name=None,
                            remaining_seat=3,
                            provider_uid=self.alibaba,
                            one_adult_redirect_url="alibaba.ir/one_adult_redirect_url",
                            two_adult_redirect_url=None,
                            base_redirect_url="alibaba.ir"
                        ),
                    ]

                )
            )
        )

        self.service.on_event_or_command(
            emitter_claim=accounts_interfaces.Session.for_internal_app(uid='flight_crawler_service'),
            event_or_command=event_bus_interfaces.EventOrCommand(
                uid=str(uuid4()),
                event_type='CRAWLED_FLIGHT',
                payload=flight_crawler_interfaces.CrawlResponse(
                    uid=str(uuid4()),
                    crawl_timestamp=current_timestamp,
                    origin='THR',
                    destination='TBZ',
                    results=[
                        flight_crawler_interfaces.Flight(
                            airline='iran air',
                            flight_number='10',
                            departure_timestamp=self.current_timestamp + 13,
                            arrival_timestamp=self.current_timestamp + 24,
                            seat_class='Economy',
                            allowed_weight=20,
                            adult_price=300,
                            child_price=300,
                            infant_price=100,
                            airplane_name=None,
                            remaining_seat=3,
                            provider_uid=self.alibaba,
                            one_adult_redirect_url="alibaba.ir/one_adult_redirect_url",
                            two_adult_redirect_url=None,
                            base_redirect_url="alibaba.ir"
                        ),
                        flight_crawler_interfaces.Flight(
                            airline='iran air tour',
                            flight_number='10',
                            departure_timestamp=self.current_timestamp + 13,
                            arrival_timestamp=self.current_timestamp + 24,
                            seat_class='Economy',
                            allowed_weight=20,
                            adult_price=300,
                            child_price=300,
                            infant_price=100,
                            airplane_name=None,
                            remaining_seat=3,
                            provider_uid=self.alibaba,
                            one_adult_redirect_url="alibaba.ir/one_adult_redirect_url",
                            two_adult_redirect_url=None,
                            base_redirect_url="alibaba.ir"
                        ),
                    ]

                )
            )
        )


    def test_happy(self): 
        results = self.service.get_favorite_cities(
            request=interfaces.GetFavoriteCitiesRequest(
                origin=None
            )
        )

        print(F"\n\nresults ===>>> {results}\n\n")

