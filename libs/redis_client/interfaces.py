from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class ICacheService(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """
        Retrieve the string value stored at the specified key.

        :param key: The cache key.
        :return: The string value if it exists, else None.
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """
        Set a value for the given key in the cache.

        :param key: The cache key.
        :param value: The value to store.
        :param ex: Optional expiration time in seconds.
        :return: True if the operation was successful.
        """
        pass

    @abstractmethod
    def set_json(self, key: str, value: Any, ex: Optional[int] = None) -> None:
        """
        Set a dictionary value (converted to JSON) in the cache.

        :param key: The cache key.
        :param value: The dictionary to store.
        :param ex: Optional expiration time in seconds.
        """
        pass

    @abstractmethod
    def get_json(self, key: str) -> Optional[dict]:
        """
        Retrieve and parse a JSON object from the cache.

        :param key: The cache key.
        :return: The dictionary if exists, else None.
        """
        pass

    @abstractmethod
    def mget(self, keys: List[str]) -> List[Optional[str]]:
        """
        Retrieve multiple string values for the given list of keys.

        :param keys: List of cache keys.
        :return: List of string values or None for missing keys.
        """
        pass

    @abstractmethod
    def mget_json(self, keys: List[str]) -> List[Optional[Dict[str, Any]]]:
        """
        Retrieve multiple JSON objects for the given keys.

        :param keys: List of cache keys.
        :return: List of dictionaries or None for missing keys.
        """
        pass

    @abstractmethod
    def mset(self, mapping: Dict[str, Any]) -> bool:
        """
        Set multiple key-value pairs in the cache.

        :param mapping: A dictionary of key-value pairs to store.
        :return: True if operation is successful.
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> int:
        """
        Delete a key from the cache.

        :param key: The cache key to delete.
        :return: Number of keys deleted (0 or 1).
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.

        :param key: The cache key.
        :return: True if the key exists, else False.
        """
        pass

    @abstractmethod
    def expire(self, key: str, ttl: int) -> bool:
        """
        Set a TTL (expiration time) for a given key.

        :param key: The cache key.
        :param ttl: Expiration time in seconds.
        :return: True if TTL was set successfully.
        """
        pass

    @abstractmethod
    def flush_db(self) -> None:
        """
        Clear all data from the current Redis database.

        :return: None
        """
        pass

    @abstractmethod
    def incr(self, key: str, amount: int = 1) -> int:
        """
        Atomically increment the integer value of a key.

        :param key: The cache key.
        :param amount: The increment amount (default: 1).
        :return: The new value after incrementing.
        """
        pass

    @abstractmethod
    def ttl(self, key: str) -> int:
        """
        Get the remaining TTL (time to live) of a key.

        :param key: The cache key.
        :return: TTL in seconds. -1 means no TTL, -2 means key does not exist.
        """
        pass
