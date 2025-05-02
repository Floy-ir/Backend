from rest_framework import viewsets, permissions, response
from runner.bootstrap import get_bootstrapper
from . import interfaces as interfaces
import logging

logger = logging.getLogger(__name__)


class FlightsViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        service = get_bootstrapper().get_flights_service()
        filters = interfaces.GetFlightsRequest(**request.query_params.dict())
        results = service.get_flights(request=filters)
        return response.Response(results.model_dump())

    def get_cheapest_ticket(self, request):
        service = get_bootstrapper().get_flights_service()
        cheapest_request = interfaces.GetCheapestTicketRequest(**request.query_params.dict())
        results = service.get_cheapest_ticket(request=cheapest_request)
        return response.Response(results.model_dump())
