import logging
from uuid import uuid4
from .models import Airline
from typing import Dict
from . import interfaces
from apps.accounts import interfaces as accounts_interfaces
from libs.redis_client import interfaces as cache_interfaces
from apps.file_storage import interfaces as file_storage_interfaces
from libs.normalizer import normalize_airline

logger = logging.getLogger(__name__)


class AirlineService(interfaces.AbstractAirlineService):
    def __init__(
            self,
            claim: accounts_interfaces.Session,
            file_storage_service: file_storage_interfaces.AbstractFileStorageService,
            cache_service: cache_interfaces.ICacheService
    ):
        self.claim = claim
        self.file_storage = file_storage_service
        self.cache_service = cache_service

    def get_airline(self, uid: str) -> interfaces.AirlineDTO:
        cached_airline = self.cache_service.get_json(uid)

        if cached_airline:
            logger.debug(f"Cache hit for airline with uid {uid}")
            result = self._convert_dict_to_airline(cached_airline)
            logger.info(f"result: {result}")
            return result

        try:
            airline = Airline.objects.get(uid=uid)
        except Airline.DoesNotExist:
            logger.debug(f"airline with uid {uid} doesn't exist")
            raise interfaces.AirlineNotFound()

        result = self._convert_airline_to_dataclass(airline)
        self.cache_service.set_json(uid, result.model_dump())
        logger.info(f"result: {result}")
        return result

    def get_airlines(self, request: interfaces.AirlineListReq) -> Dict[str, interfaces.AirlineDTO]:
        logger.info(f"request: {request}")
        cached_airlines = self.cache_service.mget_json(request.uid_list)

        print(f'\n\ncached_airlines: {cached_airlines}\n\n')

        result = {}
        missing_uids = []

        for uid, airline in zip(request.uid_list, cached_airlines):
            if airline is None:
                missing_uids.append(uid)
                continue

            result[uid] = self._convert_dict_to_airline(airline)

        if not missing_uids:
            return result

        logger.debug(f"Cache miss for airlines with uids: {','.join(missing_uids)}")
        airlines = Airline.objects.filter(uid__in=missing_uids)

        for airline in airlines:
            result[airline.uid] = self._convert_airline_to_dataclass(airline)
            self.cache_service.set_json(airline.uid, result[airline.uid].model_dump())

        return result

    def upload_image(self, request: interfaces.UploadImageReq) -> interfaces.AirlineDTO:
        logger.debug(f"Request: {request}")

        try:
            airline = Airline.objects.get(uid=request.uid)
        except Airline.DoesNotExist:
            logger.debug(f"Airline with uid {request.uid} doesn't exist")
            raise interfaces.AirlineNotFound()

        try:
            image_link = self.file_storage.upload_files(
                caller=self.claim,
                request=file_storage_interfaces.UploadRequest(
                    uid=request.uid,
                    files=[request.image]
                )
            )
        except file_storage_interfaces.InternalFileStorageNotAvailable as e:
            logger.debug(f"Error: {e}")
            raise interfaces.FileStorageNotAvailable()

        airline.image = image_link.results[0]
        airline.save()

        result = self._convert_airline_to_dataclass(airline)
        self.cache_service.set_json(request.uid, result.model_dump())

        logger.debug(f"Result: {result}")
        return result

    def get_airline_by_name(self, name: str) -> interfaces.AirlineDTO:
        logger.debug(f"Searching for airline with name containing: '{name}'")

        normalized_name = normalize_airline(name)
        airline = Airline.objects.filter(name=normalized_name).first()

        if not airline:
            logger.info(f"Airline with name '{normalized_name}' not found. Creating new airline.")
            airline = Airline.objects.create(
                uid=str(uuid4()),
                name=normalized_name
            )
            logger.info(f"Created new airline: {airline}")

        result = self._convert_airline_to_dataclass(airline)
        logger.debug(f"Returning airline DTO: {result}")
        return result

    @staticmethod
    def _convert_airline_to_dataclass(airline: Airline) -> interfaces.AirlineDTO:
        return interfaces.AirlineDTO(
            uid=airline.uid,
            name=normalize_airline(airline.name),
            image=airline.image
        )

    @staticmethod
    def _convert_dict_to_airline(airline: dict) -> interfaces.AirlineDTO:
        return interfaces.AirlineDTO(
            name=normalize_airline(airline['name']),
            image=airline['image'],
            uid=airline['uid']
        )
