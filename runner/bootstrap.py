import logging
import os

from apps.flight_crawler.services import FlightCrawlerService
# externals
from externals.s3.services import MinioClientFactory
from externals.sms.services import MockSMSServiceFactory, MelipayamakSMSServiceFactory
# apps interfaces
from apps.accounts import interfaces as accounts_interfaces
# apps services
from apps.accounts.services import AccountService
from apps.flight_city.services import FlightCityService
from apps.file_storage.services import FileStorageService
from apps.airlines.services import AirlineService
from apps.flights.services import FlightsService
from apps.statistics.services import StatisticsService
# libs services
from libs.redis_client.services import CacheService
from utils.date_time.services import DateTimeUtils
from utils.http_requester.services import RequestsHTTPRequester

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

        _date_time_utils = kwargs.get('date_time_utils', DateTimeUtils())

        # minio
        _minio_hostname = os.getenv('MINIO_HOST', '172.20.0.7')
        _minio_port = os.getenv('MINIO_PORT', '9000')
        _minio_access_key = os.getenv('MINIO_ROOT_USER', 'minio_access_key')
        _minio_secret_key = os.getenv('MINIO_ROOT_PASSWORD', 'minio_secret_key')
        _minio_bucket_name = os.getenv('MINIO_BUCKET_NAME', 'floy-bucket')
        _minio_secure = os.getenv('MINIO_SECURE', 'false').lower() == 'true'
        _minio_public_url = os.getenv('MINIO_PUBLIC_URL', f'http://{_minio_hostname}:{_minio_port}')

        # redis
        _REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
        _REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
        _REDIS_DB = int(os.getenv('REDIS_DB', '0'))

        # SMS service configuration
        _melipayamak_api_key = os.getenv('MELIPAYAMAK_API_KEY', '')
        _melipayamak_sender = os.getenv('MELIPAYAMAK_SENDER', '')
        
        # Create SMS service factory
        if _melipayamak_api_key and _melipayamak_sender:
            logger.info("Using Melipayamak SMS service")
            _sms_service_factory = kwargs.get(
                'sms_service_factory',
                MelipayamakSMSServiceFactory(
                    api_key=_melipayamak_api_key,
                    sender=_melipayamak_sender
                )
            )
        else:
            logger.warning("MELIPAYAMAK_API_KEY or MELIPAYAMAK_SENDER not configured, using Mock SMS service")
            _sms_service_factory = kwargs.get('sms_service_factory', MockSMSServiceFactory())

        # variables
        _max_adults = 2

        # externals
        _s3_client_factory = kwargs.get("s3_client_factory", MinioClientFactory(
            hostname=f"{_minio_hostname}:{_minio_port}",
            access_key=_minio_access_key,
            secret_key=_minio_secret_key,
            bucket_name=_minio_bucket_name,
            secure=_minio_secure,
            public_url=_minio_public_url
        ))

        _http_requester = kwargs.get('http_requester', RequestsHTTPRequester())

        # cache
        self._cache_service = kwargs.get(
            'cache_service',
            CacheService(
                hostname=_REDIS_HOST,
                port=_REDIS_PORT,
                db=_REDIS_DB,
            )
        )

        # apps
        self._account_service = kwargs.get(
            'account_service',
            AccountService(
                sms_service_factory=_sms_service_factory,
                date_time=_date_time_utils,
            )
        )

        self._file_storage_service = kwargs.get(
            'file_storage_service',
            FileStorageService(
                claim=accounts_interfaces.Session.for_internal_app(uid='file_storage_service'),
                date_time_utils=_date_time_utils,
                minio_bucket_name=_minio_bucket_name,
                s3_client_factory=_s3_client_factory,
                minio_public_url=_minio_public_url
            ))

        self._flight_city_service = kwargs.get(
            'flight_city_service',
            FlightCityService(
            claim=accounts_interfaces.Session.for_internal_app(uid='flight_city_service'),
        ))

        self._airlines_service = kwargs.get(
            'airlines_service',
            AirlineService(
                claim=accounts_interfaces.Session.for_internal_app(uid='airlines_service'),
                file_storage_service=self._file_storage_service,
                cache_service=self._cache_service,
            )
        )

        self._flights_service = kwargs.get(
            'flights_service',
            FlightsService(
                claim=accounts_interfaces.Session.for_internal_app(uid='airlines_service'),
                airlines_service=self._airlines_service,
                date_time_utils=_date_time_utils,
                flight_crawler_service=None,  # Will be set after crawler is created
                cache_service=self._cache_service
            )
        )

        self._flight_crawler_service = kwargs.get(
            'flight_crawler_service',
            FlightCrawlerService(
                claim=accounts_interfaces.Session.for_internal_app(uid='flight_crawler_service'),
                date_time_utils=_date_time_utils,
                flights_service=self._flights_service,
                flight_city_service=self._flight_city_service,
                file_storage_service=self._file_storage_service,
                http_requester=_http_requester,
                cache_service=self._cache_service,
                airline_service=self._airlines_service,
                max_adults=_max_adults
            )
        )

        # Update flights service with crawler service
        self._flights_service.flight_crawler_service = self._flight_crawler_service

        self._statistics_service = kwargs.get(
            'statistics_service',
            StatisticsService(
                claim=accounts_interfaces.Session.for_internal_app(uid='statistics_service'),
            )
        )


    def get_account_service(self) -> AccountService:
        return self._account_service

    def get_flight_city_service(self):
        return self._flight_city_service

    def get_file_storage_service(self) -> FileStorageService:
        return self._file_storage_service

    def get_airlines_service(self) -> AirlineService:
        return self._airlines_service

    def get_cache_service(self) -> CacheService:
        return self._cache_service

    def get_flights_service(self) -> FlightsService:
        return self._flights_service

    def get_flight_crawler_service(self) -> FlightCrawlerService:
        return self._flight_crawler_service
    
    def get_statistics_service(self) -> StatisticsService:
        return self._statistics_service

    def get_date_time_utils(self) -> DateTimeUtils:
        return self._date_time_utils


    def cleanup(self):
        """Cleanup resources to prevent memory leaks"""
        import gc
        try:
            # Close HTTP session if it exists
            if hasattr(self._flight_crawler_service, 'http_requester') and hasattr(self._flight_crawler_service.http_requester, 'session'):
                self._flight_crawler_service.http_requester.session.close()
            
            # Close Redis connection
            from libs.redis_client.client import RedisClient
            RedisClient.close_client()
            
            # Force garbage collection
            gc.collect()
            logger.info("Bootstrap cleanup completed")
        except Exception as e:
            logger.warning(f"Error during bootstrap cleanup: {e}")


def get_bootstrapper(**kwargs) -> Bootstrapper:
        bootstrapper = Bootstrapper(**kwargs)
        return bootstrapper
