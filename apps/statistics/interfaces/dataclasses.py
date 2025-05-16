from libs import dataclasses
from typing import List



class Statistic(dataclasses.BaseModel):
    provider: str
    redirect_number: int


class IncreaseRedirectNumberRequest(dataclasses.BaseModel):
    provider: str


class GetProvidersInfo(dataclasses.BaseModel):
    count: int
    results: List[Statistic]