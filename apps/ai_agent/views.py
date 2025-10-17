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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ai_agent_service = None

    @property
    def ai_agent_service(self):
        """Lazy initialization of AI agent service"""
        if self._ai_agent_service is None:
            bootstrapper = get_bootstrapper()
            
            # Get OpenAI API key from settings
            openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY not configured in settings")
            
            self._ai_agent_service = interfaces.AIAgentService(
                claim=accounts_interfaces.Session(),  # Anonymous session for now
                flights_service=bootstrapper.get_flights_service(),
                cities_service=bootstrapper.get_flight_city_service(),
                airlines_service=bootstrapper.get_airline_service(),
                date_time_utils=bootstrapper.get_date_time_utils(),
                openai_api_key=openai_api_key
            )
        return self._ai_agent_service

    @action(detail=False, methods=['post'])
    def chat(self, request):
        """Main chat endpoint for AI agent"""
        try:
            message = request.data.get('message', '').strip()
            session_id = request.data.get('session_id', str(uuid.uuid4()))
            
            if not message:
                return response.Response(
                    {"error": "Message is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create or get conversation context
            context = interfaces.ConversationContext(
                session_id=session_id,
                last_updated=datetime.now()
            )
            
            # Process the message
            ai_response = self.ai_agent_service.process_user_message(message, context)
            
            return response.Response({
                "message": ai_response.message,
                "intent": ai_response.intent.model_dump() if ai_response.intent else None,
                "search_results": ai_response.search_results,
                "requires_clarification": ai_response.requires_clarification,
                "clarification_questions": ai_response.clarification_questions,
                "session_id": session_id
            })
            
        except Exception as e:
            logger.error(f"Error in chat endpoint: {str(e)}")
            return response.Response(
                {"error": "An error occurred while processing your request"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def conversation(self, request):
        """Conversation endpoint with message history and system instructions"""
        try:
            messages_data = request.data.get('messages', [])
            system_instructions = request.data.get('system_instructions', None)
            
            if not messages_data:
                return response.Response(
                    {"error": "Messages are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Convert message data to ConversationMessage objects
            messages = []
            for msg_data in messages_data:
                if isinstance(msg_data, dict) and 'role' in msg_data and 'content' in msg_data:
                    messages.append(interfaces.ConversationMessage(
                        role=msg_data['role'],
                        content=msg_data['content'],
                        timestamp=datetime.fromisoformat(msg_data.get('timestamp', datetime.now().isoformat()))
                    ))
                else:
                    return response.Response(
                        {"error": "Invalid message format. Each message must have 'role' and 'content' fields"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Process the conversation
            ai_response = self.ai_agent_service.process_conversation(messages, system_instructions)
            
            return response.Response({
                "message": ai_response.message,
                "intent": ai_response.intent.model_dump() if ai_response.intent else None,
                "search_results": ai_response.search_results,
                "requires_clarification": ai_response.requires_clarification,
                "clarification_questions": ai_response.clarification_questions
            })
            
        except Exception as e:
            logger.error(f"Error in conversation endpoint: {str(e)}")
            return response.Response(
                {"error": "An error occurred while processing the conversation"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def search_flights(self, request):
        """Direct flight search endpoint"""
        try:
            search_request = interfaces.FlightSearchRequest(**request.data)
            results = self.ai_agent_service.search_flights(search_request)
            
            return response.Response(results)
            
        except Exception as e:
            logger.error(f"Error in search_flights endpoint: {str(e)}")
            return response.Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def get_cheapest_flights(self, request):
        """Get cheapest flights endpoint"""
        try:
            search_request = interfaces.CheapestFlightSearchRequest(**request.data)
            results = self.ai_agent_service.get_cheapest_flights(search_request)
            
            return response.Response(results)
            
        except Exception as e:
            logger.error(f"Error in get_cheapest_flights endpoint: {str(e)}")
            return response.Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def search_cities(self, request):
        """Search cities endpoint"""
        try:
            query = request.query_params.get('query', '')
            search_request = interfaces.CitySearchRequest(query=query if query else None)
            results = self.ai_agent_service.search_cities(search_request)
            
            return response.Response(results)
            
        except Exception as e:
            logger.error(f"Error in search_cities endpoint: {str(e)}")
            return response.Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def search_airlines(self, request):
        """Search airlines endpoint"""
        try:
            query = request.query_params.get('query', '')
            search_request = interfaces.AirlineSearchRequest(query=query if query else None)
            results = self.ai_agent_service.search_airlines(search_request)
            
            return response.Response(results)
            
        except Exception as e:
            logger.error(f"Error in search_airlines endpoint: {str(e)}")
            return response.Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def get_function_schema(self, request):
        """Get OpenAI function calling schema for external use"""
        try:
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
            
        except Exception as e:
            logger.error(f"Error in get_function_schema endpoint: {str(e)}")
            return response.Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
