import logging
import json
import openai
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import re

from . import interfaces
from apps.flights import interfaces as flights_interfaces
from apps.flight_city import interfaces as cities_interfaces
from apps.airlines import interfaces as airlines_interfaces
from apps.accounts import interfaces as accounts_interfaces
from utils.date_time import interfaces as date_time_interfaces
from runner.bootstrap import get_bootstrapper

logger = logging.getLogger(__name__)


class AIAgentService(interfaces.AbstractAIAgentService):
    """AI Agent service for flight booking assistance"""
    
    def __init__(
        self,
        claim: accounts_interfaces.Session,
        flights_service: flights_interfaces.AbstractFlightsService,
        cities_service: cities_interfaces.AbstractFlightCityService,
        airlines_service: airlines_interfaces.AbstractAirlineService,
        date_time_utils: date_time_interfaces.AbstractDateTime,
        openai_api_key: str
    ):
        self.claim = claim
        self.flights_service = flights_service
        self.cities_service = cities_service
        self.airlines_service = airlines_service
        self.date_time_utils = date_time_utils
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        
        # OpenAI function calling schema
        self.functions = [
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

    def process_user_message(self, message: str, context: interfaces.ConversationContext) -> interfaces.AIAgentResponse:
        """Process user message and return AI response with flight data"""
        try:
            # Extract travel intent using OpenAI
            intent = self.extract_travel_intent(message)
            
            # Determine if we need to search for flights
            search_results = None
            if intent.origin and intent.destination and intent.departure_date:
                search_results = self._perform_flight_search(intent)
            
            # Generate response
            response_message = self.generate_response(intent, search_results)
            
            # Check if clarification is needed
            requires_clarification = self._needs_clarification(intent)
            clarification_questions = self._get_clarification_questions(intent) if requires_clarification else None
            
            return interfaces.AIAgentResponse(
                message=response_message,
                intent=intent,
                search_results=search_results,
                requires_clarification=requires_clarification,
                clarification_questions=clarification_questions
            )
            
        except Exception as e:
            logger.error(f"Error processing user message: {str(e)}")
            return interfaces.AIAgentResponse(
                message="I apologize, but I encountered an error while processing your request. Please try again or rephrase your question.",
                requires_clarification=True,
                clarification_questions=["Could you please tell me where you want to travel from and to?"]
            )

    def extract_travel_intent(self, message: str, system_instructions: Optional[str] = None) -> interfaces.TravelIntent:
        """Extract travel intent from user message using OpenAI"""
        try:
            default_system_prompt = """You are a flight booking assistant. Extract travel information from the user's message.
            
            Extract the following information if mentioned:
            - Origin city (convert to city codes like THR, MHD, IFN, etc.)
            - Destination city (convert to city codes)
            - Departure date (convert to YYYY-MM-DD format)
            - Return date (for round trips)
            - Seat class preference
            - Price range
            - Airline preferences
            - Number of passengers
            - Trip type (one_way, round_trip, multi_city)
            
            If dates are relative (like "tomorrow", "next week"), convert them to actual dates.
            If only partial information is provided, set other fields to null.
            
            IMPORTANT: If the user doesn't provide origin, destination, or departure date, you must politely ask for the missing information. Be helpful and conversational in your response.
            """
            
            system_prompt = system_instructions or default_system_prompt
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                functions=self.functions,
                function_call="auto",
                temperature=0.1
            )
            
            # Parse the response to extract intent
            intent = self._parse_intent_from_response(response, message)
            return intent
            
        except Exception as e:
            logger.error(f"Error extracting travel intent: {str(e)}")
            return interfaces.TravelIntent()

    def process_conversation(self, messages: List[interfaces.ConversationMessage], system_instructions: Optional[str] = None) -> interfaces.AIAgentResponse:
        """Process conversation with message history and system instructions"""
        try:
            # Prepare messages for OpenAI
            openai_messages = []
            
            # Add system instructions if provided
            if system_instructions:
                openai_messages.append({"role": "system", "content": system_instructions})
            
            # Convert conversation messages to OpenAI format
            for msg in messages:
                openai_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Get the last user message for intent extraction
            last_user_message = None
            for msg in reversed(messages):
                if msg.role == "user":
                    last_user_message = msg.content
                    break
            
            if not last_user_message:
                return interfaces.AIAgentResponse(
                    message="I didn't receive a user message to process.",
                    requires_clarification=True,
                    clarification_questions=["Could you please tell me how I can help you with your travel plans?"]
                )
            
            # Extract travel intent from the conversation context
            intent = self.extract_travel_intent(last_user_message, system_instructions)
            
            # Determine if we need to search for flights
            search_results = None
            if intent.origin and intent.destination and intent.departure_date:
                search_results = self._perform_flight_search(intent)
            
            # Generate response using conversation context
            response_message = self._generate_conversational_response(
                openai_messages, intent, search_results, system_instructions
            )
            
            # Check if clarification is needed
            requires_clarification = self._needs_clarification(intent)
            clarification_questions = self._get_clarification_questions(intent) if requires_clarification else None
            
            return interfaces.AIAgentResponse(
                message=response_message,
                intent=intent,
                search_results=search_results,
                requires_clarification=requires_clarification,
                clarification_questions=clarification_questions
            )
            
        except Exception as e:
            logger.error(f"Error processing conversation: {str(e)}")
            return interfaces.AIAgentResponse(
                message="I apologize, but I encountered an error while processing our conversation. Please try again.",
                requires_clarification=True,
                clarification_questions=["Could you please rephrase your request?"]
            )

    def search_flights(self, request: interfaces.FlightSearchRequest) -> Dict[str, Any]:
        """Search flights based on criteria"""
        try:
            flights_request = flights_interfaces.GetFlightsRequest(
                origin=request.origin,
                destination=request.destination,
                departure_timestamp__gte=request.departure_timestamp_gte,
                departure_timestamp__lte=request.departure_timestamp_lte,
                arrival_timestamp__gte=request.arrival_timestamp_gte,
                arrival_timestamp__lte=request.arrival_timestamp_lte,
                seat_classes=request.seat_classes,
                price__lte=request.max_price,
                price__gte=request.min_price,
                airlines=request.airlines,
                remaining_seats__gte=request.remaining_seats_min
            )
            
            result = self.flights_service.get_flights(flights_request)
            return result.model_dump()
            
        except Exception as e:
            logger.error(f"Error searching flights: {str(e)}")
            return {"error": str(e), "count": 0, "results": []}

    def get_cheapest_flights(self, request: interfaces.CheapestFlightSearchRequest) -> Dict[str, Any]:
        """Get cheapest flights for a route"""
        try:
            cheapest_request = flights_interfaces.GetCheapestTicketRequest(
                origin=request.origin,
                destination=request.destination,
                reference_date=request.reference_date,
                forward_day=request.forward_days,
                backward_day=request.backward_days
            )
            
            result = self.flights_service.get_cheapest_ticket(cheapest_request)
            return result.model_dump()
            
        except Exception as e:
            logger.error(f"Error getting cheapest flights: {str(e)}")
            return {"error": str(e), "count": 0, "results": []}

    def search_cities(self, request: interfaces.CitySearchRequest) -> Dict[str, Any]:
        """Search cities by name or code"""
        try:
            cities_request = cities_interfaces.GetCitiesRequest()
            result = self.cities_service.get_cities(cities_request)
            
            # Filter results if query is provided
            if request.query:
                query_lower = request.query.lower()
                filtered_results = []
                for city in result.results:
                    if (query_lower in city.name.lower() or 
                        query_lower in city.value.lower()):
                        filtered_results.append(city)
                result.results = filtered_results
                result.count = len(filtered_results)
            
            return result.model_dump()
            
        except Exception as e:
            logger.error(f"Error searching cities: {str(e)}")
            return {"error": str(e), "count": 0, "results": []}

    def search_airlines(self, request: interfaces.AirlineSearchRequest) -> Dict[str, Any]:
        """Search airlines by name"""
        try:
            # Get all airlines (you might want to implement a search method in airlines service)
            airlines_request = airlines_interfaces.AirlineListReq(uid_list=[])
            result = self.airlines_service.get_airlines(airlines_request)
            
            # Filter results if query is provided
            if request.query:
                query_lower = request.query.lower()
                filtered_results = {}
                for uid, airline in result.items():
                    if query_lower in airline.name.lower():
                        filtered_results[uid] = airline
                result = filtered_results
            
            return {"airlines": result}
            
        except Exception as e:
            logger.error(f"Error searching airlines: {str(e)}")
            return {"error": str(e), "airlines": {}}

    def generate_response(self, intent: interfaces.TravelIntent, search_results: Optional[Dict[str, Any]] = None) -> str:
        """Generate natural language response based on intent and results"""
        try:
            if not search_results:
                return self._generate_no_results_response(intent)
            
            if "error" in search_results:
                return f"I encountered an error while searching for flights: {search_results['error']}"
            
            count = search_results.get("count", 0)
            results = search_results.get("results", [])
            
            if count == 0:
                return self._generate_no_flights_found_response(intent)
            
            # Generate response based on results
            response = f"I found {count} flight(s) for your trip from {intent.origin} to {intent.destination}.\n\n"
            
            # Show top 3 results
            for i, flight in enumerate(results[:3]):
                airline_name = flight.get("airline", {}).get("name", "Unknown Airline")
                price = flight.get("cheapest_price", 0)
                seat_class = flight.get("seat_class", "Economy")
                departure_time = self._format_timestamp(flight.get("departure_timestamp", 0))
                
                response += f"{i+1}. {airline_name} - {seat_class} - ${price:.2f}\n"
                response += f"   Departure: {departure_time}\n"
                response += f"   From: {flight.get('origin')} → To: {flight.get('destination')}\n\n"
            
            if count > 3:
                response += f"... and {count - 3} more flights available.\n"
            
            response += "Would you like me to show you more details about any of these flights or help you with booking?"
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I found some flights for you, but I'm having trouble formatting the details. Please try asking again."

    def _perform_flight_search(self, intent: interfaces.TravelIntent) -> Dict[str, Any]:
        """Perform flight search based on intent"""
        try:
            # Convert dates to timestamps
            departure_timestamp_gte = self.date_time_utils.convert_datetime_string_to_timestamp(
                intent.departure_date, '%Y-%m-%d'
            )
            
            # Add flexibility if requested
            if intent.flexible_dates and intent.date_flexibility_days:
                flexibility_seconds = intent.date_flexibility_days * 24 * 60 * 60
                departure_timestamp_lte = departure_timestamp_gte + flexibility_seconds
            else:
                departure_timestamp_lte = departure_timestamp_gte + (24 * 60 * 60)  # Next day
            
            # Create search request
            search_request = interfaces.FlightSearchRequest(
                origin=intent.origin,
                destination=intent.destination,
                departure_timestamp_gte=departure_timestamp_gte,
                departure_timestamp_lte=departure_timestamp_lte,
                seat_classes=[intent.seat_class] if intent.seat_class else None,
                max_price=intent.max_price,
                min_price=intent.min_price,
                airlines=intent.airline_preference
            )
            
            return self.search_flights(search_request)
            
        except Exception as e:
            logger.error(f"Error performing flight search: {str(e)}")
            return {"error": str(e)}

    def _parse_intent_from_response(self, response, original_message: str) -> interfaces.TravelIntent:
        """Parse travel intent from OpenAI response"""
        try:
            # Extract function call if present
            if response.choices[0].message.function_call:
                function_call = response.choices[0].message.function_call
                function_args = json.loads(function_call.arguments)
                
                return interfaces.TravelIntent(
                    origin=function_args.get("origin"),
                    destination=function_args.get("destination"),
                    departure_date=function_args.get("departure_date"),
                    return_date=function_args.get("return_date"),
                    seat_class=function_args.get("seat_class"),
                    max_price=function_args.get("max_price"),
                    airline_preference=function_args.get("airline_preference"),
                    passengers=function_args.get("passengers", 1)
                )
            else:
                # Try to extract basic info from the message
                return self._extract_basic_intent(original_message)
                
        except Exception as e:
            logger.error(f"Error parsing intent: {str(e)}")
            return interfaces.TravelIntent()

    def _extract_basic_intent(self, message: str) -> interfaces.TravelIntent:
        """Extract basic travel intent from message using regex patterns"""
        intent = interfaces.TravelIntent()
        
        # Simple patterns for common travel phrases
        origin_patterns = [
            r"from\s+([A-Z]{3})",
            r"leaving\s+([A-Z]{3})",
            r"departing\s+([A-Z]{3})"
        ]
        
        destination_patterns = [
            r"to\s+([A-Z]{3})",
            r"going\s+to\s+([A-Z]{3})",
            r"destination\s+([A-Z]{3})"
        ]
        
        for pattern in origin_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                intent.origin = match.group(1).upper()
                break
        
        for pattern in destination_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                intent.destination = match.group(1).upper()
                break
        
        return intent

    def _needs_clarification(self, intent: interfaces.TravelIntent) -> bool:
        """Check if clarification is needed"""
        return not (intent.origin and intent.destination and intent.departure_date)

    def _get_clarification_questions(self, intent: interfaces.TravelIntent) -> List[str]:
        """Get clarification questions based on missing information"""
        questions = []
        
        if not intent.origin:
            questions.append("Where would you like to travel from?")
        if not intent.destination:
            questions.append("Where would you like to travel to?")
        if not intent.departure_date:
            questions.append("When would you like to travel?")
        
        return questions

    def _generate_no_results_response(self, intent: interfaces.TravelIntent) -> str:
        """Generate response when no search was performed"""
        if not intent.origin and not intent.destination:
            return "I'd be happy to help you find flights! Could you please tell me where you'd like to travel from and to?"
        elif not intent.origin:
            return f"I can help you find flights to {intent.destination}. Could you please tell me which city you'll be traveling from?"
        elif not intent.destination:
            return f"I can help you find flights from {intent.origin}. Could you please tell me which city you'd like to travel to?"
        elif not intent.departure_date:
            return f"I can help you find flights from {intent.origin} to {intent.destination}. When would you like to travel?"
        else:
            return "I'm ready to search for flights. Please provide your travel details."

    def _generate_no_flights_found_response(self, intent: interfaces.TravelIntent) -> str:
        """Generate response when no flights are found"""
        return f"I couldn't find any flights from {intent.origin} to {intent.destination} for {intent.departure_date}. " \
               f"Would you like me to search for alternative dates or nearby airports?"

    def _format_timestamp(self, timestamp: int) -> str:
        """Format timestamp to readable date/time"""
        try:
            return self.date_time_utils.convert_timestamp_to_date(timestamp, '%Y-%m-%d %H:%M')
        except:
            return "Unknown date"

    def _generate_conversational_response(
        self, 
        openai_messages: List[Dict[str, str]], 
        intent: interfaces.TravelIntent, 
        search_results: Optional[Dict[str, Any]] = None,
        system_instructions: Optional[str] = None
    ) -> str:
        """Generate conversational response using OpenAI with context"""
        try:
            # Create a response generation prompt
            response_prompt = """Based on the conversation history and flight search results, provide a helpful and natural response to the user's travel request.
            
            Guidelines:
            - Be conversational and helpful
            - If flight results are available, summarize the key options
            - If no flights are found, suggest alternatives
            - Ask clarifying questions if information is missing
            - Keep responses concise but informative
            - Use the flight data to provide specific details like prices, airlines, and times
            
            IMPORTANT: If the user hasn't provided origin, destination, or departure date, politely ask for the missing information. Be helpful and conversational in your response.
            """
            
            # Add the response prompt as a system message
            messages_with_prompt = [
                {"role": "system", "content": response_prompt}
            ] + openai_messages
            
            # Add search results context if available
            if search_results and search_results.get("results"):
                results_summary = f"Flight search results: Found {search_results.get('count', 0)} flights. "
                if search_results.get("results"):
                    first_flight = search_results["results"][0]
                    results_summary += f"Cheapest option: {first_flight.get('airline', {}).get('name', 'Unknown')} for ${first_flight.get('cheapest_price', 0)}"
                messages_with_prompt.append({
                    "role": "system", 
                    "content": f"Context: {results_summary}"
                })
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages_with_prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating conversational response: {str(e)}")
            # Fallback to basic response generation
            return self.generate_response(intent, search_results)
