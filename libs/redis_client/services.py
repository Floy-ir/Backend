from .interfaces import ICacheService
from typing import List, Optional, Any
from .client import RedisClient
import json

class CacheService(ICacheService):
    def __init__(self, hostname: str, port: int, db: int):
        self.redis = RedisClient().get_client(host=hostname, port=port, db=db)

    def get(self, key: str) -> Optional[str]:
        return self.redis.get(key)

    def set_json(self, key: str, value: Any, ex: Optional[int] = None):
        json_value = json.dumps(value)
        self.redis.set(key, json_value, ex=ex)

    def get_json(self, key: str) -> Optional[dict]:
        value = self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    def mget_json(self, keys: List[str]) -> List[Optional[Dict[str, Any]]]:
        """
        Get multiple keys and parse their JSON values.
        Returns list of dictionaries or None for missing keys.
        """
        values = self.redis.mget(keys)
        return [json.loads(v) if v else None for v in values]

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """
        ex: expiration time in seconds
        """
        return self.redis.set(key, value, ex=ex)

    def delete(self, key: str) -> int:
        return self.redis.delete(key)

    def mget(self, keys: List[str]) -> List[Optional[str]]:
        return self.redis.mget(keys)

    def mset(self, mapping: dict[str, Any]) -> bool:
        return self.redis.mset(mapping)

    def exists(self, key: str) -> bool:
        return self.redis.exists(key) > 0

    def expire(self, key: str, ttl: int) -> bool:
        return self.redis.expire(key, ttl)

    def flush_db(self) -> None:
        self.redis.flushdb()

    def incr(self, key: str, amount: int = 1) -> int:
        return self.redis.incr(key, amount)

    def ttl(self, key: str) -> int:
        return self.redis.ttl(key)
