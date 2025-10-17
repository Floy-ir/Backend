import abc
from typing import Dict, Any, Optional, List
from . import dataclasses


class AbstractAIAgentService(abc.ABC):
    """Abstract interface for AI Agent service"""
    
    @abc.abstractmethod
    def process_user_message(self, message: str, context: dataclasses.ConversationContext) -> dataclasses.AIAgentResponse:
        """Process user message and return AI response with flight data"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def extract_travel_intent(self, message: str) -> dataclasses.TravelIntent:
        """Extract travel intent from user message using AI"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def search_flights(self, request: dataclasses.FlightSearchRequest) -> Dict[str, Any]:
        """Search flights based on criteria"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_cheapest_flights(self, request: dataclasses.CheapestFlightSearchRequest) -> Dict[str, Any]:
        """Get cheapest flights for a route"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def search_cities(self, request: dataclasses.CitySearchRequest) -> Dict[str, Any]:
        """Search cities by name or code"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def search_airlines(self, request: dataclasses.AirlineSearchRequest) -> Dict[str, Any]:
        """Search airlines by name"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def generate_response(self, intent: dataclasses.TravelIntent, search_results: Optional[Dict[str, Any]] = None) -> str:
        """Generate natural language response based on intent and results"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def process_conversation(self, messages: List[dataclasses.ConversationMessage], system_instructions: Optional[str] = None) -> dataclasses.AIAgentResponse:
        """Process conversation with message history and system instructions"""
        raise NotImplementedError
