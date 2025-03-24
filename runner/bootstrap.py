import logging
# externals
from externals.s3.services import MinioClientFactory
# apps interfaces
from apps.accounts import interfaces as accounts_interfaces
# apps services
from apps.flight_city.services import FlightCityService
from apps.file_storage.services import FileStorageService
from apps.airlines.services import AirlineService
from apps.flights.services import FlightsService
# libs services
from libs.redis_client.services import CacheService

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

        # minio
        _minio_hostname = 'minio_hostname'
        _minio_access_key = 'minio_access_key'
        _minio_secret_key = 'minio_secret_key'
        _minio_bucket_name = 'minio_bucket_name'

        # redis
        _REDIS_HOST = "localhost"
        _REDIS_PORT = 6379
        _REDIS_DB = 0

        # externals
        _s3_client_factory = kwargs.get("s3_client_factory", MinioClientFactory(
            hostname=_minio_hostname,
            access_key=_minio_access_key,
            secret_key=_minio_secret_key,
            bucket_name=_minio_bucket_name
        ))

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
        self._file_storage_service = kwargs.get(
            'file_storage_service',
            FileStorageService(
                claim=accounts_interfaces.Session.for_internal_app(uid='file_storage_service'),
                # date_time_utils=_date_time_utils,
                minio_bucket_name=_minio_bucket_name,
                s3_client_factory=_s3_client_factory,
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
            )
        )

        self._flights_service = kwargs.get(
            'flights_service',
            FlightsService(
                claim=accounts_interfaces.Session.for_internal_app(uid='airlines_service'),
                airlines_service=self._airlines_service
            )
        )


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

def get_bootstrapper(**kwargs) -> Bootstrapper:
        bootstrapper = Bootstrapper(**kwargs)
        return bootstrapper
