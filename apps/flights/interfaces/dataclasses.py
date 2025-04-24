from libs import dataclasses
from typing import List
from enum import Enum
from typing import Dict


class SeatClass(str, Enum):
    FIRST_CLASS = 'First'
    BUSINESS_CLASS = 'Business'
    PREMIUM_ECONOMY = 'Premium Economy'
    ECONOMY_CLASS = 'Economy'
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
    websites: List[str] | None = None
    price__lte: float | None = None
    price__gte: float | None = None
    remaining_seats__gte: int | None = 0


class AirlineDetail(dataclasses.BaseModel):
    uid: dataclasses.UUIDField
    name: str
    image: dataclasses.URLField | None = None


class WebsiteDetail(dataclasses.BaseModel):
    uid: dataclasses.UUIDField
    name: str
    name_fa: str
    image: dataclasses.URLField | None = None


class WebsiteDTO(dataclasses.BaseModel):
    uid: WebsiteDetail
    adult_price: float
    child_price: float | None = None
    infant_price: float | None = None
    base_redirect_url: dataclasses.URLField
    one_adult_redirect_url: dataclasses.URLField | None = None
    two_adult_redirect_url: dataclasses.URLField | None = None
    remaining_seat: int


class FlightDTO(dataclasses.BaseModel):
    airline: AirlineDetail
    origin: str
    destination: str
    departure_timestamp: int
    arrival_timestamp: int
    allowed_weight: int
    seat_class: SeatClass
    websites: List[WebsiteDTO]


class FlightWithoutWebsiteDTO(dataclasses.BaseModel):
    airline: AirlineDetail
    origin: str
    destination: str
    departure_timestamp: int
    arrival_timestamp: int
    allowed_weight: int
    seat_class: SeatClass
    price: float
    redirect_url: dataclasses.URLField
    website: WebsiteDetail


class AirlineFilters(dataclasses.BaseModel):
    uid: dataclasses.UUIDField
    name: str
    logo: dataclasses.URLField
    min_price: float


class WebsiteFilters(dataclasses.BaseModel):
    uid: dataclasses.UUIDField
    name: str
    name_fa: str
    logo: dataclasses.URLField
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
    results: List[FlightDTO]


class GetCheapestTicketRequest(dataclasses.BaseModel):
    origin: str
    destination: str
    reference_timestamp: int
    forward_day: int
    backward_day: int


class GetCheapestResponse(dataclasses.BaseModel):
    count: int
    results: List[FlightWithoutWebsiteDTO]

