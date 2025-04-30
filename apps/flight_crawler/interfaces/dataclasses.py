from libs import dataclasses as lib_dataclasses
from typing import List


class CrawlRequest(lib_dataclasses.BaseModel):
    origin: str
    destination: str
    departure_timestamp: int
    adult: int
    child: int
    infant: int


class WebsiteDTO(lib_dataclasses.BaseModel):
    uid: lib_dataclasses.UUIDField
    name: str
    name_fa: str
    logo: lib_dataclasses.URLField | None = None


class GetWebsitesRequest(lib_dataclasses.BaseModel):
    uid_list: List[lib_dataclasses.UUIDField]



class UploadImageRequest(lib_dataclasses.BaseModel):
    uid: lib_dataclasses.UUIDField
    logo: lib_dataclasses.File


class Flight(lib_dataclasses.BaseModel):
    airline: str
    flight_number: str
    departure_timestamp: int
    arrival_timestamp: int
    seat_class: str #TODO
    allowed_weight: int
    adult_price: float
    child_price: float | None = None
    infant_price: float | None = None
    airplane_name: str | None = None
    remaining_seat: int | None = None 
    provider_uid: lib_dataclasses.UUIDField
    one_adult_redirect_url: lib_dataclasses.URLField | None = None 
    two_adult_redirect_url: lib_dataclasses.URLField | None = None 
    base_redirect_url: lib_dataclasses.URLField | None = None


class CrawlResponse(lib_dataclasses.BaseModel):
    uid: lib_dataclasses.UUIDField
    crawl_timestamp: int
    origin: str
    destination: str
    results: List[Flight]
