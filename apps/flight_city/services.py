import logging
from . import interfaces
from apps.accounts import interfaces as accounts_interfaces
from .models import City


logger = logging.getLogger(__name__)


class FileStorageService(interfaces.AbstractFlightCityService):
    def __init__(
            self,
            claim: accounts_interfaces.Session,
    ) -> None:
        self.claim = claim

    def create_city(self, request: interfaces.CreateCityRequest):
        City.objects.create(
            name=request.name,
            value=request.value
        )

    def add_destination(self, request: interfaces.AddDestinationRequest):
        src_obj = City.objects.get(value=request.src_value)
        City.objects.filter(origin=src_obj).update(origin_city=None)
        new_dest_cities = City.objects.filter(value__in=request.dest_value_list)
        new_dest_cities.update(origin_city=src_obj)


    def get_cities(self, request: interfaces.GetCitiesRequest) -> interfaces.CityList:
        cities = City.objects.prefetch_related('destinations')

        return interfaces.CityList(
            count=len(cities),
            results=[self._convert_city_to_src_city(city) for city in cities],
        )


    def get_city(self, request: interfaces.GetCityRequest) -> interfaces.GetCityResponse:
        city = City.objects.get(value=request.value)

        return self._convert_city_to_city_response_dto(city)


    def _convert_city_to_src_city(self, city: City) -> interfaces.SrcCity:
        return interfaces.SrcCity(
            name=city.name,
            value=city.value,
            destinations=self._convert_city_to_dto_city(city.destinations.all()),
        )

    def _convert_city_to_city_response_dto(self, city: interfaces.CityDTO) -> interfaces.GetCityResponse:
        return interfaces.GetCityResponse(
            name=city.name,
            value=city.value,
            destinations=self._convert_city_to_dto_city(city.destinations.all()),
        )

    @staticmethod
    def _convert_city_to_dto_city(city: City) -> interfaces.CityDTO:
        return interfaces.CityDTO(
            name=city.name,
            value=city.value,
        )

