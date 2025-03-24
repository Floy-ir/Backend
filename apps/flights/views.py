from rest_framework import viewsets, permissions, response
from runner.bootstrap import get_bootstrapper
from . import interfaces as interfaces


class FlightsViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        service = get_bootstrapper().get_flights_service()
        filters = interfaces.GetFlightsRequest(**request.query_params.dict())
        results = service.get_flights(request=filters)
        return response.Response(results.model_dump())
