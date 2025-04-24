from uuid import uuid4
from django.test import TestCase
from apps.accounts import interfaces as accounts_interfaces
from apps.event_bus import interfaces as event_bus_interfaces
from apps.flight_crawler import interfaces as flight_crawler_interfaces
from runner.bootstrap import get_bootstrapper


class EventCommandTestCase(TestCase): 
    def setUp(self) -> None:

        self.alibaba = str(uuid4())
        self.flightio = str(uuid4())
        self.pate = str(uuid4())
        
        bootstrapper = get_bootstrapper(

        )

        self.service = bootstrapper.get_flights_service()
        self.service.on_event_or_command(
            emitter_claim=accounts_interfaces.Session.for_internal_app(uid='flight_crawler_service'),
            event_or_command=event_bus_interfaces.EventOrCommand(
                uid=str(uuid4()),
                event_type='',
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
                            airline='qeshm',
                            flight_number='11',
                            departure_timestamp=13,
                            arrival_timestamp=24,
                            seat_class='Economy',
                            allowed_weight=25,
                            adult_price=1000,
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
                            departure_timestamp=13,
                            arrival_timestamp=24,
                            seat_class='Economy',
                            allowed_weight=25,
                            adult_price=1000,
                            child_price=500,
                            infant_price=200,
                            airplane_name=None,
                            remaining_seat=1,
                            provider_uid=self.flightio,
                            one_adult_redirect_url=None,
                            two_adult_redirect_url="flightio.com/two_adult_redirect_url",
                            base_redirect_url="flightio.com"
                        ),
                        flight_crawler_interfaces.Flight(
                            airline='Iranair',
                            flight_number='12',
                            departure_timestamp=13,
                            arrival_timestamp=24,
                            seat_class='Economy',
                            allowed_weight=30,
                            adult_price=1500,
                            child_price=500,
                            infant_price=200,
                            airplane_name=None,
                            remaining_seat=2,
                            provider_uid=self.pate,
                            one_adult_redirect_url="pateh.com/one_adult_redirect_url",
                            two_adult_redirect_url=None,
                            base_redirect_url="pate.com"
                        ),
                    ]

                )
            )
        )


    def test_happy(self): 
        pass
