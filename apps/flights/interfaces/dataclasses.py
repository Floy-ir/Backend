from libs import dataclasses
from typing import List
from enum import Enum


class SeatClass(str, Enum):
    FIRST_CLASS = 'First Class'
    BUSINESS_CLASS = 'Business Class'
    PREMIUM_ECONOMY = 'Premium Economy'
    ECONOMY_CLASS = 'Economy Class'
    BASIC_ECONOMY = 'Basic Economy'


class GetFlightsRequest(dataclasses.BaseModel):
    # flights filters
    airlines: List[dataclasses.UUIDField] | None = None
    origin: str
    destination: str
    departure_time: int
    arrival_time: int | None = None
    allowed_weights: List[int] | None = None
    seat_classes: List[SeatClass] | None = None
    # website filters
    price__lte: float | None = None
    price__gte: float | None = None
    remaining_seats__gte: int | None = 0
    is_valid: bool | None = True


class GetFlightsResponse(dataclasses.BaseModel):
    pass


class CreateFlightRequest(dataclasses.BaseModel):
    pass