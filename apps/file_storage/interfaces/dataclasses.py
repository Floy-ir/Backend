from typing import List
from pydantic import field_validator
from libs import dataclasses as lib_dataclasses


class UploadRequest(lib_dataclasses.BaseModel):
    uid: str
    files: List[lib_dataclasses.File]

    @field_validator('files')
    def validate_files_not_empty(cls, v):
        if not v:  # If list is empty
            raise ValueError('files list cannot be empty')
        return v

    class Config:
        arbitrary_types_allowed = True


class FileMetadata(lib_dataclasses.BaseModel):
    file_name: str  # todo: remove??
    file_size_in_bytes: int


class UploadMetadata(lib_dataclasses.BaseModel):
    uid: str
    uploaded_at: int
    uploaded_by: str
    files: List[FileMetadata]


class UploadMetadataResult(lib_dataclasses.BaseModel):
    count: int
    results: List[UploadMetadata]


class ImagesLink(lib_dataclasses.BaseModel):
    count: int
    results: List[str]
