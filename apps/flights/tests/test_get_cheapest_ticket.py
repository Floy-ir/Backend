from django.test import TestCase
from apps.accounts import interfaces as accounts_interfaces
from apps.event_bus import interfaces as event_bus_interfaces
from apps.flight_crawler import interfaces as flight_crawler_interfaces
from .fake_modules import *
from .. import interfaces
from runner.bootstrap import get_bootstrapper
from uuid import uuid4
from constants import SECOND_IN_A_DAY


class GetCheapestTicketTestCase(TestCase):
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
                            arrival_timestamp=15,
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
                        )
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
                    crawl_timestamp=73800,
                    origin='THR',
                    destination='MHD',
                    results=[
                        flight_crawler_interfaces.Flight(
                            airline='qeshm',
                            flight_number='11',
                            departure_timestamp=73801,
                            arrival_timestamp=73802,
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
                    crawl_timestamp=160200,
                    origin='THR',
                    destination='MHD',
                    results=[
                        flight_crawler_interfaces.Flight(
                            airline='Iranair',
                            flight_number='12',
                            departure_timestamp=160200,
                            arrival_timestamp=160202,
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
                                

    def test_get_cheapest_ticket_happy(self):
        # Test getting cheapest tickets for a 3-day period
        results = self.service.get_cheapest_ticket(
            request=interfaces.GetCheapestTicketRequest(
                origin='THR',
                destination='MHD',
                reference_date='1348-10-11',
                forward_day=4,  # Search 3 days forward
                backward_day=0  # Don't search backward
            )
        )

        # Verify the count
        self.assertEqual(results.count, 4)

        # Verify the first result (cheapest flight)
        result1 = results.results[0]
        self.assertEqual(result1.origin, 'THR')
        self.assertEqual(result1.destination, 'MHD')
        self.assertEqual(result1.date, '1348-10-11')
        self.assertEqual(result1.price, 1000.0)

        # Verify the second result
        result2 = results.results[1]
        self.assertEqual(result2.price, 1100.0)

        # Verify the third result
        result3 = results.results[2]
        self.assertEqual(result3.price, 1500.0)

        # Verify the fourth result
        result4 = results.results[3]
        self.assertEqual(result4.price, 0)

    def test_get_cheapest_ticket_happy_with_backward_day(self):
        # Test getting cheapest tickets for a 3-day period
        results = self.service.get_cheapest_ticket(
            request=interfaces.GetCheapestTicketRequest(
                origin='THR',
                destination='MHD',
                reference_date='1348-10-12',
                forward_day=3,  # Search 3 days forward
                backward_day=1  # Don't search backward
            )
        )

        # Verify the count
        self.assertEqual(results.count, 4)

        # Verify the first result (cheapest flight)
        result1 = results.results[0]
        self.assertEqual(result1.origin, 'THR')
        self.assertEqual(result1.destination, 'MHD')
        self.assertEqual(result1.date, '1348-10-11')
        self.assertEqual(result1.price, 1000.0)

        # Verify the second result
        result2 = results.results[1]
        self.assertEqual(result2.origin, 'THR')
        self.assertEqual(result2.destination, 'MHD')
        self.assertEqual(result2.date, '1348-10-12')
        self.assertEqual(result2.price, 1100.0)

        # Verify the third result
        result3 = results.results[2]
        self.assertEqual(result3.origin, 'THR')
        self.assertEqual(result3.destination, 'MHD')
        self.assertEqual(result3.date, '1348-10-13')
        self.assertEqual(result3.price, 1500.0)

        # Verify the fourth result
        result4 = results.results[3]
        self.assertEqual(result4.origin, 'THR')
        self.assertEqual(result4.destination, 'MHD')
        self.assertEqual(result4.date, '1348-10-14')
        self.assertEqual(result4.price, 0)
