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

        # Get favorite_cities from query params and handle if it doesn't exist
        favorite_cities = request.query_params.get('favorite_cities', '')
        
        # Split the cities and clean up the list
        favorite_cities_list = [city.strip() for city in favorite_cities.split(',') if city.strip()]
        
        logger.debug(f"favorite_cities ==>> {favorite_cities_list}")
        cheapest_favorite_city_date_request = interfaces.GetFavoriteCitiesRequest(
            favorite_cities=favorite_cities_list
        )
        
        logger.info(f"Request object ==>> {cheapest_favorite_city_date_request}")
        results = service.get_favorite_cities(request=cheapest_favorite_city_date_request)
        return response.Response(results.model_dump())
