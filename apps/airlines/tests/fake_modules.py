# fake modules for tests
from apps.accounts import interfaces as accounts_interfaces
from libs.redis_client import interfaces as cache_interfaces
from apps.file_storage import interfaces as file_storage_interfaces
import json
from typing import Dict, Any


class FakeCacheService(cache_interfaces.ICacheService):
    def __init__(self):
        self.cache = {}

    def get(self, key: str) -> Any:
        return json.loads(self.cache.get(key))

    def set(self, key: str, value: Any, ttl: int = 3600):
        self.cache[key] = json.dumps(value)

    def delete(self, key: str):
        del self.cache[key]

    def clear(self):
        self.cache.clear()

    def exists(self, key: str) -> bool:
        pass

    def expire(self, key: str, seconds: int) -> bool:
        pass

    def flush_db(self) -> None:
        pass

    def get_json(self, key: str) -> Any:
        pass

    def incr(self, key: str, amount: int = 1) -> int:
        pass

    def mget(self, keys: list[str]) -> list[Any]:
        pass

    def mget_json(self, keys: list[str]) -> list[Any]:
        return [json.loads(self.cache[key]) if key in self.cache else None for key in keys]

    def mset(self, mapping: dict[str, Any]) -> None:    
        pass

    def set_json(self, key: str, value: Any, ttl: int = 3600) -> None:
        self.cache[key] = json.dumps(value)

    def ttl(self, key: str) -> int:
        pass



class FakeFileStorageService(file_storage_interfaces.AbstractFileStorageService):
    def __init__(self):
        self.files = {}

    def upload_files(self, caller: accounts_interfaces.Session, request: file_storage_interfaces.UploadRequest) -> file_storage_interfaces.ImagesLink:
        return file_storage_interfaces.ImagesLink(
            count=len(request.files),
            results=[f"https://example.com/{request.uid}/{file.name}" for file in request.files]
        )
    
    
    def get_images_link(self, uid: str) -> file_storage_interfaces.ImagesLink:
        pass

    def get_file_metadata(self, uid: str) -> file_storage_interfaces.FileMetadata:
        pass

    def get_file_metadata_list(self, uids: list[str]) -> list[file_storage_interfaces.FileMetadata]:
        pass
