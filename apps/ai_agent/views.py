import logging
import uuid
from datetime import datetime
from rest_framework import viewsets, permissions, response, status
from rest_framework.decorators import action
from django.conf import settings

from runner.bootstrap import get_bootstrapper
from . import interfaces
from apps.accounts import interfaces as accounts_interfaces

logger = logging.getLogger(__name__)


class AIAgentViewSet(viewsets.GenericViewSet):
    """AI Agent ViewSet for flight booking assistance"""
    permission_classes = [permissions.AllowAny]

    def chat(self, request):
        """Main chat endpoint for AI agent"""
        service = get_bootstrapper().get_ai_agent_service()
        chat_request = interfaces.ChatRequest(**request.data)
        
        # Create conversation context
        context = interfaces.ConversationContext(
            session_id=chat_request.session_id or str(uuid.uuid4()),
            last_updated=datetime.now()
        )
        
        results = service.process_user_message(chat_request.message, context)
        return response.Response(results.model_dump())

    def conversation(self, request):
        """Conversation endpoint with message history and system instructions"""
        service = get_bootstrapper().get_ai_agent_service()
        conversation_request = interfaces.ConversationRequest(**request.data)
        results = service.process_conversation(conversation_request.messages, conversation_request.system_instructions)
        return response.Response(results.model_dump())

    def search_flights(self, request):
        """Direct flight search endpoint"""
        service = get_bootstrapper().get_ai_agent_service()
        search_request = interfaces.FlightSearchRequest(**request.data)
        results = service.search_flights(search_request)
        return response.Response(results)

    def get_cheapest_flights(self, request):
        """Get cheapest flights endpoint"""
        service = get_bootstrapper().get_ai_agent_service()
        search_request = interfaces.CheapestFlightSearchRequest(**request.data)
        results = service.get_cheapest_flights(search_request)
        return response.Response(results)

    def search_cities(self, request):
        """Search cities endpoint"""
        service = get_bootstrapper().get_ai_agent_service()
        query = request.query_params.get('query', '')
        search_request = interfaces.CitySearchRequest(query=query if query else None)
        results = service.search_cities(search_request)
        return response.Response(results)

    def search_airlines(self, request):
        """Search airlines endpoint"""
        service = get_bootstrapper().get_ai_agent_service()
        query = request.query_params.get('query', '')
        search_request = interfaces.AirlineSearchRequest(query=query if query else None)
        results = service.search_airlines(search_request)
        return response.Response(results)

    def get_function_schema(self, request):
        """Get OpenAI function calling schema for external use"""
        # Return the function schema that can be used with OpenAI
        functions = [
            {
                "name": "search_flights",
                "description": "Search for flights between two cities with specific criteria",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "Origin city code (e.g., 'THR', 'MHD', 'IFN')"
                        },
                        "destination": {
                            "type": "string", 
                            "description": "Destination city code (e.g., 'THR', 'MHD', 'IFN')"
                        },
                        "departure_date": {
                            "type": "string",
                            "description": "Departure date in YYYY-MM-DD format"
                        },
                        "return_date": {
                            "type": "string",
                            "description": "Return date in YYYY-MM-DD format (for round trips)"
                        },
                        "seat_class": {
                            "type": "string",
                            "enum": ["Economy", "Premium Economy", "Business", "First"],
                            "description": "Preferred seat class"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Maximum price limit"
                        },
                        "airline_preference": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Preferred airlines"
                        },
                        "passengers": {
                            "type": "integer",
                            "description": "Number of passengers",
                            "default": 1
                        }
                    },
                    "required": ["origin", "destination", "departure_date"]
                }
            },
            {
                "name": "get_cheapest_flights",
                "description": "Find the cheapest flights for a route within a date range",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "Origin city code"
                        },
                        "destination": {
                            "type": "string",
                            "description": "Destination city code"
                        },
                        "reference_date": {
                            "type": "string",
                            "description": "Reference date in YYYY-MM-DD format"
                        },
                        "forward_days": {
                            "type": "integer",
                            "description": "Days to search forward from reference date",
                            "default": 7
                        },
                        "backward_days": {
                            "type": "integer", 
                            "description": "Days to search backward from reference date",
                            "default": 7
                        }
                    },
                    "required": ["origin", "destination", "reference_date"]
                }
            },
            {
                "name": "search_cities",
                "description": "Search for cities by name or get all available cities",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "City name or code to search for"
                        }
                    }
                }
            },
            {
                "name": "search_airlines",
                "description": "Search for airlines by name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Airline name to search for"
                        }
                    }
                }
            }
        ]
        
        return response.Response({
            "functions": functions,
            "description": "AI Agent function calling schema for flight booking assistance"
        })
