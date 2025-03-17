import logging

from rest_framework import viewsets, permissions, response
from runner.bootstrap import get_bootstrapper
from . import interfaces as interfaces


logger = logging.getLogger(__name__)

class FlightCityViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        service = get_bootstrapper().get_flight_city_service()
        request = interfaces.GetCitiesRequest(**request.data)
        result = service.get_cities(request=request)
        return response.Response(result.model_dump())
