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

    def get_cheapest_favorite_city_date(self, request):
        service = get_bootstrapper().get_flights_service()
        
        # Handle list query parameters
        query_params = request.query_params.copy()
        if 'favorite_cities' in query_params:
            favorite_cities = []
            favorite_cities.extend(query_params.get('favorite_cities', '').split(','))
            
            # Remove empty strings and strip whitespace
            favorite_cities = [city.strip() for city in favorite_cities if city.strip()]
            
            query_params = query_params.copy()
            query_params.setlist('favorite_cities', favorite_cities)
        
        cheapest_favorite_city_date_request = interfaces.GetFavoriteCitiesRequest(**query_params.dict())
        results = service.get_favorite_cities(request=cheapest_favorite_city_date_request)
        return response.Response(results.model_dump())
