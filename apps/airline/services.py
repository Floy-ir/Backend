import logging
from uuid import uuid4
from .models import Airline
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

    def get_airlines(self, request: interfaces.AirlineListReq) -> interfaces.Airlines:
        airlines = Airline.objects.filter(uid__in=request.uid_list)

        return interfaces.Airlines(
            count=airlines.count(),
            results=[]
        )

    def upload_image(self, request: interfaces.AirlineUploadReq) -> interfaces.Airlines:
        pass

    def get_airline_by_name(self, name: str) -> interfaces.AirlineDTO:
        airline = Airline.objects.filter(name__contains=name).first()

        if airline is None:
            logger.debug(f"carrier with title {name} doesn't exist")
            airline = Airline.objects.create(
                uid=str(uuid4()),
                name=name
            )
            logger.debug(f"carrier with title {name} create")

        result = self._convert_airline_to_dataclass(airline)
        return result

    @staticmethod
    def _convert_airline_to_dataclass(airline: Airline) -> interfaces.AirlineDTO:
        return interfaces.AirlineDTO(
            uid=airline.uid,
            name=airline.name,
            images=airline.image
        )
