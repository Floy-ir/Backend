import redis
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    _client = None

    @classmethod
    def get_client(cls, host, port, db, decode_responses=True):
        if cls._client is None:
            cls._client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,  # Returns string instead of bytes
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
                max_connections=20
            )
        return cls._client

    @classmethod
    def close_client(cls):
        """Close the Redis client connection"""
        if cls._client is not None:
            try:
                cls._client.close()
                logger.info("Redis client connection closed")
            except Exception as e:
                logger.warning(f"Error closing Redis client: {e}")
            finally:
                cls._client = None
