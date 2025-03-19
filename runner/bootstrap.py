import os
import logging
# externals
from externals.s3.services import MinioClientFactory
# apps interfaces
from apps.flight_city import interfaces as flight_city_interfaces
from apps.accounts import interfaces as accounts_interfaces
# apps services
from apps.flight_city.services import FlightCityService
from apps.file_storage.services import FileStorageService

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

        # externals
        _s3_client_factory = kwargs.get("s3_client_factory", MinioClientFactory(
            hostname=_minio_hostname,
            access_key=_minio_access_key,
            secret_key=_minio_secret_key,
            bucket_name=_minio_bucket_name
        ))

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
            claim=accounts_interfaces.Session.for_internal_app(uid='flight_city'),
        ))

    def get_flight_city_service(self):
        return self._flight_city_service

    def get_file_storage_service(self) -> FileStorageService:
        return self._file_storage_service

def get_bootstrapper(**kwargs) -> Bootstrapper:
        bootstrapper = Bootstrapper(**kwargs)
        return bootstrapper
