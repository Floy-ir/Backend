from libs import dataclasses
from typing import List, Optional, Dict, Any
from datetime import datetime


class TravelIntent(dataclasses.BaseModel):
    """Represents a user's travel intention extracted from natural language"""
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    seat_class: Optional[str] = None
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    airline_preference: Optional[List[str]] = None
    trip_type: Optional[str] = None  # "one_way", "round_trip", "multi_city"
    passengers: Optional[int] = 1
    flexible_dates: Optional[bool] = False
    date_flexibility_days: Optional[int] = 3


class FlightSearchRequest(dataclasses.BaseModel):
    """Request for searching flights"""
    origin: str
    destination: str
    departure_timestamp_gte: int
    departure_timestamp_lte: int
    arrival_timestamp_gte: Optional[int] = None
    arrival_timestamp_lte: Optional[int] = None
    seat_classes: Optional[List[str]] = None
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    airlines: Optional[List[str]] = None
    remaining_seats_min: Optional[int] = 1


class CheapestFlightSearchRequest(dataclasses.BaseModel):
    """Request for finding cheapest flights"""
    origin: str
    destination: str
    reference_date: str
    forward_days: int = 7
    backward_days: int = 7


class CitySearchRequest(dataclasses.BaseModel):
    """Request for searching cities"""
    query: Optional[str] = None


class AirlineSearchRequest(dataclasses.BaseModel):
    """Request for searching airlines"""
    query: Optional[str] = None


class AIAgentResponse(dataclasses.BaseModel):
    """Response from AI agent"""
    message: str
    intent: Optional[TravelIntent] = None
    search_results: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    requires_clarification: bool = False
    clarification_questions: Optional[List[str]] = None


class ConversationMessage(dataclasses.BaseModel):
    """Represents a single message in conversation"""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: datetime = datetime.now()


class ConversationContext(dataclasses.BaseModel):
    """Context for maintaining conversation state"""
    user_id: Optional[str] = None
    session_id: str
    previous_intents: List[TravelIntent] = []
    current_intent: Optional[TravelIntent] = None
    conversation_history: List[ConversationMessage] = []
    system_instructions: Optional[str] = None
    last_updated: datetime = datetime.now()
