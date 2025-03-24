import logging
from uuid import uuid4
from .models import Airline
from typing import Dict
from . import interfaces
from apps.accounts import interfaces as accounts_interfaces
from apps.file_storage import interfaces as file_storage_interfaces

logger = logging.getLogger(__name__)

class AirlineService(interfaces.AbstractAirlineService):
    def __init__(
            self,
            claim: accounts_interfaces.Session,
            file_storage_service: file_storage_interfaces.AbstractFileStorageService,
    ):
        self.claim = claim
        self.file_storage = file_storage_service

    def get_airline(
            self,
            uid: str
    ) -> interfaces.AirlineDTO:
        try:
            carrier = Airline.objects.get(uid=uid)
        except Airline.DoesNotExist:
            logger.debug(f"carrier with uid {uid} doesn't exist")
            raise interfaces.AirlineNotFound()

        result = self._convert_airline_to_dataclass(carrier)
        return result

    def get_airlines(self, request: interfaces.AirlineListReq) -> Dict[str, interfaces.AirlineDTO]:
        airlines = Airline.objects.filter(uid__in=request.uid_list)

        return {
            airline.uid: self._convert_airline_to_dataclass(airline)
            for airline in airlines
        }

    def upload_image(self, request: interfaces.UploadImageReq) -> interfaces.AirlineDTO:
        # TODO: check caller or not?!
        logger.debug(f"request: {request}")

        airline = None
        try:
            airline = Airline.objects.get(uid=request.uid)
        except Airline.DoesNotExist:
            logger.debug(f"airline with uid {request.uid} doesn't exist")
            raise interfaces.AirlineNotFound()

        image_link = None
        try:
            image_link = self.file_storage.upload_files(
                caller=self.claim,
                request=file_storage_interfaces.UploadRequest(
                    uid=request.uid,
                    files=[request.image]
                )
            )
        except file_storage_interfaces.InternalFileStorageNotAvailable as e:
            logger.debug(f"error: {e}")
            raise interfaces.FileStorageNotAvailable()

        airline.image = image_link
        airline.save()

        result = self._convert_airline_to_dataclass(airline)
        logger.debug(f"result: {result}")
        return result

    def get_airline_by_name(self, name: str) -> interfaces.AirlineDTO:
        logger.debug(f"Searching for airline with name containing: '{name}'")

        airline = Airline.objects.filter(name__icontains=name).first()

        if not airline:
            logger.info(f"Airline with name '{name}' not found. Creating new airline.")
            airline = Airline.objects.create(
                uid=str(uuid4()),
                name=name
            )
            logger.info(f"Created new airline: {airline}")

        result = self._convert_airline_to_dataclass(airline)
        logger.debug(f"Returning airline DTO: {result}")
        return result

    @staticmethod
    def _convert_airline_to_dataclass(airline: Airline) -> interfaces.AirlineDTO:
        return interfaces.AirlineDTO(
            uid=airline.uid,
            name=airline.name,
            images=airline.image
        )
