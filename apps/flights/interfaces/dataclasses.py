from libs import dataclasses
from typing import List
from enum import Enum
from typing import Dict


class SeatClass(str, Enum):
    FIRST_CLASS = 'First Class'
    BUSINESS_CLASS = 'Business Class'
    PREMIUM_ECONOMY = 'Premium Economy'
    ECONOMY_CLASS = 'Economy Class'
    BASIC_ECONOMY = 'Basic Economy'


class GetFlightsRequest(dataclasses.BaseFilter):
    # flights filters
    airlines: List[dataclasses.UUIDField] | None = None
    origin: str
    destination: str
    departure_timestamp__gte: int
    departure_timestamp__lte: int
    arrival_timestamp__gte: int | None = None
    arrival_timestamp__lte: int | None = None
    allowed_weights: List[int] | None = None
    seat_classes: List[SeatClass] | None = None
    # website filters
    website_uids: List[str] | None = None
    price__lte: float | None = None
    price__gte: float | None = None
    remaining_seats__gte: int | None = 0
    is_valid: bool | None = True


class Airline(dataclasses.BaseModel):
    uid: dataclasses.UUIDField
    name: str
    image: dataclasses.URLField | None = None


class WebsiteDTO(dataclasses.BaseModel):
    uid: dataclasses.UUIDField # TODO: return detail
    price: float
    redirect_url: dataclasses.URLField
    remaining_seat: int


class FlightDTO(dataclasses.BaseModel):
    airline: Airline
    origin: str
    destination: str
    departure_timestamp: int
    arrival_timestamp: int
    allowed_weight: int
    seat_class: SeatClass
    websites: List[WebsiteDTO]


class FlightWithoutWebsiteDTO(dataclasses.BaseModel):
    airline: dataclasses.UUIDField # TODO: return detail
    origin: str
    destination: str
    departure_timestamp: int
    arrival_timestamp: int
    allowed_weight: int
    seat_class: SeatClass
    price: float
    redirect_url: dataclasses.URLField
    website_uid: dataclasses.UUIDField


class AirlineFilters(dataclasses.BaseModel):
    uid: dataclasses.UUIDField
    name: str
    image: dataclasses.URLField
    min_price: float


class WebsiteFilters(dataclasses.BaseModel):
    uid: dataclasses.UUIDField
    name: str
    image: dataclasses.URLField
    min_price: float


class GetFlightsFilters(dataclasses.BaseModel):
    min_price: float
    max_price: float
    allowed_weights: List[int]
    seat_classes: List[SeatClass]
    airlines: List[AirlineFilters]
    websites: List[WebsiteFilters]

class GetFlightsResponse(dataclasses.BaseModel):
    count: int
    filters: GetFlightsFilters
    result: List[FlightDTO]


class GetCheapestTicketRequest(dataclasses.BaseModel):
    origin: str
    destination: str
    reference_timestamp: int
    forward_day: int


class GetCheapestResponse(dataclasses.BaseModel):
    count: int
    results: List[FlightWithoutWebsiteDTO]


class CreateFlightRequest(dataclasses.BaseModel):
    pass