from uuid import uuid4
from django.test import TestCase
from apps.accounts import interfaces as accounts_interfaces
from apps.event_bus import interfaces as event_bus_interfaces
from apps.flight_crawler import interfaces as flight_crawler_interfaces
from .fake_modules import *
from .. import interfaces
from runner.bootstrap import get_bootstrapper
from constants import SECOND_IN_A_DAY

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
        self.service.on_event_or_command(
            emitter_claim=accounts_interfaces.Session.for_internal_app(uid='flight_crawler_service'),
            event_or_command=event_bus_interfaces.EventOrCommand(
                uid=str(uuid4()),
                event_type='CRAWLED_FLIGHT',
                payload=flight_crawler_interfaces.CrawlResponse(
                    uid=str(uuid4()),
                    crawl_timestamp=10,
                    origin='THR',
                    destination='MHD',
                    results=[
                        flight_crawler_interfaces.Flight(
                            airline='kish',
                            flight_number='10',
                            departure_timestamp=13,
                            arrival_timestamp=24,
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
                            departure_timestamp=13,
                            arrival_timestamp=24,
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
                            departure_timestamp=13,
                            arrival_timestamp=24,
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
                            departure_timestamp=13,
                            arrival_timestamp=24,
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
                            departure_timestamp=16,
                            arrival_timestamp=18,
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
                            departure_timestamp=16,
                            arrival_timestamp=18,
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
                            departure_timestamp=19,
                            arrival_timestamp=21,
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


    def test_happy(self): 
        results  = self.service.get_flights(request=interfaces.GetFlightsRequest(
            origin='THR',
            destination='MHD',
            departure_timestamp__gte=9,
            departure_timestamp__lte=30
        ))


        result1 = interfaces.FlightDTO(
            airline=interfaces.AirlineDetail(
                uid='kish', 
                name='Airline kish', 
                image=None
            ), 
            origin='THR', 
            destination='MHD', 
            departure_timestamp=13, 
            arrival_timestamp=24, 
            allowed_weight=20, 
            seat_class='Economy', 
            cheapest_price=1000.0, 
            cheapest_base_redirect_url='alibaba.ir', 
            cheapest_one_adult_redirect_url='alibaba.ir/one_adult_redirect_url', 
            cheapest_two_adult_redirect_url="alibaba.ir/two_adult_redirect_url", 
            cheapest_website=interfaces.WebsiteDetail(
                uid='alibaba', 
                name='Website alibaba', 
                name_fa='Website alibaba', 
                image=None
            ), 
            websites=[
                interfaces.WebsiteDTO(
                    detail=interfaces.WebsiteDetail(
                        uid='alibaba', 
                        name='Website alibaba', 
                        name_fa='Website alibaba', 
                        image=None
                    ), 
                    adult_price=1000.0, 
                    child_price=500.0, 
                    infant_price=200.0, 
                    base_redirect_url='alibaba.ir', 
                    one_adult_redirect_url='alibaba.ir/one_adult_redirect_url', 
                    two_adult_redirect_url="alibaba.ir/two_adult_redirect_url", 
                    remaining_seat=3
                ), 
                interfaces.WebsiteDTO(
                    detail=interfaces.WebsiteDetail(
                        uid='flightio', 
                        name='Website flightio', 
                        name_fa='Website flightio', 
                        image=None
                    ), 
                    adult_price=1100.0, 
                    child_price=600.0, 
                    infant_price=100.0, 
                    base_redirect_url='flightio.com', 
                    one_adult_redirect_url='flightio.com/one_adult_redirect_url', 
                    two_adult_redirect_url="flightio.com/two_adult_redirect_url", 
                    remaining_seat=2
                ),
            ]
        )

        self.assertEqual(results.results[0], result1)

        result2 = interfaces.FlightDTO(
            airline=interfaces.AirlineDetail(
                uid='qeshm', 
                name='Airline qeshm', 
                image=None
            ), 
            origin='THR', 
            destination='MHD', 
            departure_timestamp=16, 
            arrival_timestamp=18, 
            allowed_weight=25, 
            seat_class='Economy',
            cheapest_price=1100.0, 
            cheapest_base_redirect_url='flightio.com', 
            cheapest_one_adult_redirect_url='flightio.com/one_adult_redirect_url', 
            cheapest_two_adult_redirect_url=None, 
            cheapest_website=interfaces.WebsiteDetail(
                uid='flightio', 
                name='Website flightio', 
                name_fa='Website flightio', 
                image=None
            ), 
            websites=[
                interfaces.WebsiteDTO(
                    detail=interfaces.WebsiteDetail(
                        uid='flightio', 
                        name='Website flightio', 
                        name_fa='Website flightio', 
                        image=None
                    ), 
                    adult_price=1100.0, 
                    child_price=500.0, 
                    infant_price=200.0, 
                    base_redirect_url='flightio.com', 
                    one_adult_redirect_url='flightio.com/one_adult_redirect_url', 
                    two_adult_redirect_url=None, 
                    remaining_seat=1
                ),
                interfaces.WebsiteDTO(
                    detail=interfaces.WebsiteDetail(
                        uid='pate', 
                        name='Website pate', 
                        name_fa='Website pate', 
                        image=None
                    ),
                    adult_price=1300.0, 
                    child_price=700.0, 
                    infant_price=300.0, 
                    base_redirect_url='pateh.com', 
                    one_adult_redirect_url=None, 
                    two_adult_redirect_url="pateh.com/two_adult_redirect_url", 
                    remaining_seat=1
                ),
            ]
        )

        self.assertEqual(results.results[1], result2)


        result3 = interfaces.FlightDTO(
            airline=interfaces.AirlineDetail(
                uid='Iranair', 
                name='Airline Iranair', 
                image=None
            ), 
            origin='THR', 
            destination='MHD', 
            departure_timestamp=19, 
            arrival_timestamp=21, 
            allowed_weight=30, 
            seat_class='Economy', 
            cheapest_price=1500.0,
            cheapest_base_redirect_url='pate.com', 
            cheapest_one_adult_redirect_url=None, 
            cheapest_two_adult_redirect_url=None, 
            cheapest_website=interfaces.WebsiteDetail(
                uid='pate', 
                name='Website pate', 
                name_fa='Website pate', 
                image=None
            ), 
            websites=[
                interfaces.WebsiteDTO(
                    detail=interfaces.WebsiteDetail(
                        uid='pate', 
                        name='Website pate', 
                        name_fa='Website pate', 
                        image=None
                    ), 
                    adult_price=1500.0, 
                    child_price=800.0, 
                    infant_price=400.0, 
                    base_redirect_url='pate.com', 
                    one_adult_redirect_url=None, 
                    two_adult_redirect_url=None, 
                    remaining_seat=2
                ),
            ]
        )

        self.assertEqual(results.results[2], result3)

    def test_invalid_flight(self):
        self.service.on_event_or_command(
            emitter_claim=accounts_interfaces.Session.for_internal_app(uid='flight_crawler_service'),
            event_or_command=event_bus_interfaces.EventOrCommand(
                uid=str(uuid4()),
                event_type='CRAWLED_FLIGHT',
                payload=flight_crawler_interfaces.CrawlResponse(
                    uid=str(uuid4()),
                    crawl_timestamp=10,
                    origin='THR',
                    destination='MHD',
                    results=[
                        flight_crawler_interfaces.Flight(
                            airline='qeshm',
                            flight_number='11',
                            departure_timestamp=16,
                            arrival_timestamp=18,
                            seat_class='Economy',
                            allowed_weight=25,
                            adult_price=1100,
                            child_price=500,
                            infant_price=200,
                            airplane_name=None,
                            remaining_seat=1,
                            provider_uid=self.flightio,
                            one_adult_redirect_url="flightio.com/edited_one_adult_redirect_url",
                            two_adult_redirect_url=None,
                            base_redirect_url="edited_flightio.com"
                        ),
                        flight_crawler_interfaces.Flight(
                            airline='qeshm',
                            flight_number='11',
                            departure_timestamp=16,
                            arrival_timestamp=18,
                            seat_class='Economy',
                            allowed_weight=25,
                            adult_price=1100,
                            child_price=500,
                            infant_price=200,
                            airplane_name=None,
                            remaining_seat=1,
                            provider_uid=self.flightio,
                            one_adult_redirect_url=None,
                            two_adult_redirect_url="flightio.com/edited_two_adult_redirect_url",
                            base_redirect_url="edited_flightio.com"
                        ),
                        flight_crawler_interfaces.Flight(
                            airline='qeshm',
                            flight_number='11',
                            departure_timestamp=16,
                            arrival_timestamp=18,
                            seat_class='Economy',
                            allowed_weight=25,
                            adult_price=800,
                            child_price=700,
                            infant_price=300,
                            airplane_name=None,
                            remaining_seat=1,
                            provider_uid=self.pate,
                            one_adult_redirect_url=None,
                            two_adult_redirect_url="edited_pateh.com/two_adult_redirect_url",
                            base_redirect_url="edited_pateh.com"
                        ),
                        flight_crawler_interfaces.Flight(
                            airline='Iranair',
                            flight_number='12',
                            departure_timestamp=19,
                            arrival_timestamp=21,
                            seat_class='Economy',
                            allowed_weight=30,
                            adult_price=1000,
                            child_price=900,
                            infant_price=800,
                            airplane_name=None,
                            remaining_seat=1,
                            provider_uid=self.pate,
                            one_adult_redirect_url="edited_pateh.com/one_adult_redirect_url",
                            two_adult_redirect_url="edited_pateh.com/two_adult_redirect_url",
                            base_redirect_url="edited_pateh.com"
                        ),
                    ]

                )
            )
        )

        results  = self.service.get_flights(request=interfaces.GetFlightsRequest(
            origin='THR',
            destination='MHD',
            departure_timestamp__gte=9,
            departure_timestamp__lte=30
        ))

        


        self.assertEqual(len(results.results), 2)

        result1 = interfaces.FlightDTO(
            airline=interfaces.AirlineDetail(
                uid='qeshm', 
                name='Airline qeshm', 
                image=None
            ), 
            origin='THR', 
            destination='MHD', 
            departure_timestamp=16, 
            arrival_timestamp=18, 
            allowed_weight=25, 
            seat_class='Economy',
            cheapest_price=800.0,
            cheapest_one_adult_redirect_url=None,
            cheapest_two_adult_redirect_url="edited_pateh.com/two_adult_redirect_url",
            cheapest_base_redirect_url="edited_pateh.com",
            cheapest_website=interfaces.WebsiteDetail(
                uid='pate', 
                name='Website pate', 
                name_fa='Website pate', 
                image=None
            ), 
            websites=[
                interfaces.WebsiteDTO(
                    detail=interfaces.WebsiteDetail(
                        uid='flightio', 
                        name='Website flightio', 
                        name_fa='Website flightio', 
                        image=None
                    ), 
                    adult_price=1100.0, 
                    child_price=500.0, 
                    infant_price=200.0, 
                    base_redirect_url='edited_flightio.com',
                    one_adult_redirect_url='flightio.com/edited_one_adult_redirect_url',
                    two_adult_redirect_url='flightio.com/edited_two_adult_redirect_url',
                    remaining_seat=1
                ),
                interfaces.WebsiteDTO(
                    detail=interfaces.WebsiteDetail(
                        uid='pate', 
                        name='Website pate', 
                        name_fa='Website pate', 
                        image=None
                    ),
                    adult_price=800.0, 
                    child_price=700.0, 
                    infant_price=300.0,
                    one_adult_redirect_url=None,
                    two_adult_redirect_url="edited_pateh.com/two_adult_redirect_url",
                    base_redirect_url="edited_pateh.com",
                    remaining_seat=1
                ),
            ]
        )

        self.assertEqual(results.results[0], result1)

        result2 = interfaces.FlightDTO(
            airline=interfaces.AirlineDetail(
                uid='Iranair', 
                name='Airline Iranair', 
                image=None
            ), 
            origin='THR', 
            destination='MHD', 
            departure_timestamp=19, 
            arrival_timestamp=21, 
            allowed_weight=30, 
            seat_class='Economy', 
            cheapest_price=1000.0,
            cheapest_base_redirect_url="edited_pateh.com", 
            cheapest_one_adult_redirect_url="edited_pateh.com/one_adult_redirect_url", 
            cheapest_two_adult_redirect_url="edited_pateh.com/two_adult_redirect_url", 
            cheapest_website=interfaces.WebsiteDetail(
                uid='pate', 
                name='Website pate', 
                name_fa='Website pate', 
                image=None
            ), 
            websites=[
                interfaces.WebsiteDTO(
                    detail=interfaces.WebsiteDetail(
                        uid='pate', 
                        name='Website pate', 
                        name_fa='Website pate', 
                        image=None
                    ), 
                    adult_price=1000.0,
                    child_price=900.0,
                    infant_price=800.0,
                    base_redirect_url="edited_pateh.com", 
                    one_adult_redirect_url="edited_pateh.com/one_adult_redirect_url", 
                    two_adult_redirect_url="edited_pateh.com/two_adult_redirect_url", 
                    remaining_seat=1
                ),
            ]
        )


        self.assertEqual(results.results[1], result2)

    def test_donnot_invalid_flight_in_different_day(self):
        self.service.on_event_or_command(
            emitter_claim=accounts_interfaces.Session.for_internal_app(uid='flight_crawler_service'),
            event_or_command=event_bus_interfaces.EventOrCommand(
                uid=str(uuid4()),
                event_type='CRAWLED_FLIGHT',
                payload=flight_crawler_interfaces.CrawlResponse(
                    uid=str(uuid4()),
                    crawl_timestamp=10 + SECOND_IN_A_DAY,
                    origin='THR',
                    destination='MHD',
                    results=[
                        flight_crawler_interfaces.Flight(
                            airline='qeshm',
                            flight_number='11',
                            departure_timestamp=16 + SECOND_IN_A_DAY,
                            arrival_timestamp=18 + SECOND_IN_A_DAY,
                            seat_class='Economy',
                            allowed_weight=25,
                            adult_price=800,
                            child_price=700,
                            infant_price=300,
                            airplane_name=None,
                            remaining_seat=1,
                            provider_uid=self.pate,
                            one_adult_redirect_url=None,
                            two_adult_redirect_url="edited_pateh.com/two_adult_redirect_url",
                            base_redirect_url="edited_pateh.com"
                        ),
                    ]

                )
            )
        )

        results  = self.service.get_flights(request=interfaces.GetFlightsRequest(
            origin='THR',
            destination='MHD',
            departure_timestamp__gte=10 + SECOND_IN_A_DAY,
            departure_timestamp__lte=10 + 2 * SECOND_IN_A_DAY  
        ))

        self.assertEqual(len(results.results), 1)

        result1 = interfaces.FlightDTO(
            airline=interfaces.AirlineDetail(
                uid='qeshm', 
                name='Airline qeshm', 
                image=None
            ), 
            origin='THR', 
            destination='MHD', 
            departure_timestamp=16 + SECOND_IN_A_DAY, 
            arrival_timestamp=18 + SECOND_IN_A_DAY, 
            allowed_weight=25, 
            seat_class='Economy',
            cheapest_price=800.0,
            cheapest_base_redirect_url="edited_pateh.com",
            cheapest_one_adult_redirect_url=None,
            cheapest_two_adult_redirect_url="edited_pateh.com/two_adult_redirect_url",
            cheapest_website=interfaces.WebsiteDetail(
                uid='pate', 
                name='Website pate', 
                name_fa='Website pate', 
                image=None
            ), 
            websites=[
                interfaces.WebsiteDTO(
                    detail=interfaces.WebsiteDetail(
                        uid='pate', 
                        name='Website pate', 
                        name_fa='Website pate', 
                        image=None
                    ), 
                    adult_price=800.0, 
                    child_price=700.0, 
                    infant_price=300.0, 
                    base_redirect_url="edited_pateh.com",    
                    one_adult_redirect_url=None,
                    two_adult_redirect_url="edited_pateh.com/two_adult_redirect_url",
                    remaining_seat=1
                ),
            ]
        )
        
        self.assertEqual(results.results[0], result1)

        results  = self.service.get_flights(request=interfaces.GetFlightsRequest(
            origin='THR',
            destination='MHD',
            departure_timestamp__gte=9,
            departure_timestamp__lte=30
        ))


        result1 = interfaces.FlightDTO(
            airline=interfaces.AirlineDetail(
                uid='kish', 
                name='Airline kish', 
                image=None
            ), 
            origin='THR', 
            destination='MHD', 
            departure_timestamp=13, 
            arrival_timestamp=24, 
            allowed_weight=20, 
            seat_class='Economy', 
            cheapest_price=1000.0, 
            cheapest_base_redirect_url='alibaba.ir', 
            cheapest_one_adult_redirect_url='alibaba.ir/one_adult_redirect_url', 
            cheapest_two_adult_redirect_url="alibaba.ir/two_adult_redirect_url", 
            cheapest_website=interfaces.WebsiteDetail(
                uid='alibaba', 
                name='Website alibaba', 
                name_fa='Website alibaba', 
                image=None
            ), 
            websites=[
                interfaces.WebsiteDTO(
                    detail=interfaces.WebsiteDetail(
                        uid='alibaba', 
                        name='Website alibaba', 
                        name_fa='Website alibaba', 
                        image=None
                    ), 
                    adult_price=1000.0, 
                    child_price=500.0, 
                    infant_price=200.0, 
                    base_redirect_url='alibaba.ir', 
                    one_adult_redirect_url='alibaba.ir/one_adult_redirect_url', 
                    two_adult_redirect_url="alibaba.ir/two_adult_redirect_url", 
                    remaining_seat=3
                ), 
                interfaces.WebsiteDTO(
                    detail=interfaces.WebsiteDetail(
                        uid='flightio', 
                        name='Website flightio', 
                        name_fa='Website flightio', 
                        image=None
                    ), 
                    adult_price=1100.0, 
                    child_price=600.0, 
                    infant_price=100.0, 
                    base_redirect_url='flightio.com', 
                    one_adult_redirect_url='flightio.com/one_adult_redirect_url', 
                    two_adult_redirect_url="flightio.com/two_adult_redirect_url", 
                    remaining_seat=2
                ),
            ]
        )

        self.assertEqual(results.results[0], result1)

        result2 = interfaces.FlightDTO(
            airline=interfaces.AirlineDetail(
                uid='qeshm', 
                name='Airline qeshm', 
                image=None
            ), 
            origin='THR', 
            destination='MHD', 
            departure_timestamp=16, 
            arrival_timestamp=18, 
            allowed_weight=25, 
            seat_class='Economy',
            cheapest_price=1100.0, 
            cheapest_base_redirect_url='flightio.com', 
            cheapest_one_adult_redirect_url='flightio.com/one_adult_redirect_url', 
            cheapest_two_adult_redirect_url=None, 
            cheapest_website=interfaces.WebsiteDetail(
                uid='flightio', 
                name='Website flightio', 
                name_fa='Website flightio', 
                image=None
            ), 
            websites=[
                interfaces.WebsiteDTO(
                    detail=interfaces.WebsiteDetail(
                        uid='flightio', 
                        name='Website flightio', 
                        name_fa='Website flightio', 
                        image=None
                    ), 
                    adult_price=1100.0, 
                    child_price=500.0, 
                    infant_price=200.0, 
                    base_redirect_url='flightio.com', 
                    one_adult_redirect_url='flightio.com/one_adult_redirect_url', 
                    two_adult_redirect_url=None, 
                    remaining_seat=1
                ),
                interfaces.WebsiteDTO(
                    detail=interfaces.WebsiteDetail(
                        uid='pate', 
                        name='Website pate', 
                        name_fa='Website pate', 
                        image=None
                    ),
                    adult_price=1300.0, 
                    child_price=700.0, 
                    infant_price=300.0, 
                    base_redirect_url='pateh.com', 
                    one_adult_redirect_url=None, 
                    two_adult_redirect_url="pateh.com/two_adult_redirect_url", 
                    remaining_seat=1
                ),
            ]
        )

        self.assertEqual(results.results[1], result2)


        result3 = interfaces.FlightDTO(
            airline=interfaces.AirlineDetail(
                uid='Iranair', 
                name='Airline Iranair', 
                image=None
            ), 
            origin='THR', 
            destination='MHD', 
            departure_timestamp=19, 
            arrival_timestamp=21, 
            allowed_weight=30, 
            seat_class='Economy', 
            cheapest_price=1500.0,
            cheapest_base_redirect_url='pate.com', 
            cheapest_one_adult_redirect_url=None, 
            cheapest_two_adult_redirect_url=None, 
            cheapest_website=interfaces.WebsiteDetail(
                uid='pate', 
                name='Website pate', 
                name_fa='Website pate', 
                image=None
            ), 
            websites=[
                interfaces.WebsiteDTO(
                    detail=interfaces.WebsiteDetail(
                        uid='pate', 
                        name='Website pate', 
                        name_fa='Website pate', 
                        image=None
                    ), 
                    adult_price=1500.0, 
                    child_price=800.0, 
                    infant_price=400.0, 
                    base_redirect_url='pate.com', 
                    one_adult_redirect_url=None, 
                    two_adult_redirect_url=None, 
                    remaining_seat=2
                ),
            ]
        )

        self.assertEqual(results.results[2], result3)
        
