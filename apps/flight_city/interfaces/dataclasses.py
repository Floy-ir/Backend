from typing import List
from libs import dataclasses as lib_dataclasses


class GetCitiesRequest(lib_dataclasses.BaseModel):
    pass


class CityDTO(lib_dataclasses.BaseModel):
    name: str
    value: str


class SrcCity(lib_dataclasses.BaseModel): 
    name: str
    value: str
    destinations: List[CityDTO]


class CityList(lib_dataclasses.BaseModel):
    count: int
    results: List[SrcCity]


class GetCityRequest(lib_dataclasses.BaseModel):
    value: str


class GetCityResponse(lib_dataclasses.BaseModel):
    name: str
    value: str
    destinations: List[CityDTO]


class CreateCityRequest(lib_dataclasses.BaseModel):
    name: str
    value: str

class AddDestinationRequest(lib_dataclasses.BaseModel):
    src_value: str
    dest_value_list: List[str]
