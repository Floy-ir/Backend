from libs import dataclasses
from typing import List


class UploadImageReq(dataclasses.BaseModel):
    uid: dataclasses.UUIDField
    image: dataclasses.File


class AirlineDTO(dataclasses.BaseModel):
    uid: dataclasses.UUIDField
    name: str
    image: dataclasses.URLField | None = None


class AirlineListReq(dataclasses.BaseModel):
    uid_list: List[str]


class Airlines(dataclasses.BaseModel):
    count: int
    results: List[AirlineDTO]