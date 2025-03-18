from libs import dataclasses
from typing import List


class AirlineDTO(dataclasses.BaseModel):
    uid: dataclasses.UUIDField
    name: str
    image: dataclasses.URLField | None = None


class AirlineListReq(dataclasses.BaseModel):
    uid_list: List[int]


class Airlines(dataclasses.BaseModel):
    count: int
    results: List[AirlineDTO]