import os
import logging
# apps interfaces
from apps.flight_city import interfaces as flight_city_interfaces
from apps.accounts import interfaces as accounts_interfaces
# apps services
from apps.flight_city.services import FlightCityService

logger = logging.getLogger(__name__)


class Bootstrapper:
    def __new__(cls, *args, **kwargs):
        logger.info("new method of bootstrap")
        if not hasattr(cls, 'instance') or kwargs.get('force_recreate', False):
            logger.info("create a new bootstrap")
            cls.instance = super(Bootstrapper, cls).__new__(cls)
        return cls.instance

    def __init__(self, **kwargs) -> None:
        print(f'kwargs:{kwargs}')

        self._flight_city_service = FlightCityService(
            claim=accounts_interfaces.Session.for_internal_app(uid='flight_city'),
        )

    def get_flight_city_service(self):
        return self._flight_city_service

def get_bootstrapper(**kwargs) -> Bootstrapper:
        bootstrapper = Bootstrapper(**kwargs)
        return bootstrapper
