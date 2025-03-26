from libs import dataclasses as lib_dataclasses
from typing import List


class CrawlRequest(lib_dataclasses.BaseModel):
    origin: str
    destination: str
    departure_time: int


class CrawlResponse(lib_dataclasses.BaseModel):
    pass


class Website(lib_dataclasses.BaseModel):
    uid: lib_dataclasses.UUIDField
    name: str
    name_fa: str
    logo: lib_dataclasses.URLField


class GetWebsitesRequest(lib_dataclasses.BaseModel):
    uid_list: List[lib_dataclasses.UUIDField]



class UploadPhotoRequest(lib_dataclasses.BaseModel):
    uid: lib_dataclasses.UUIDField
    logo: lib_dataclasses.File

