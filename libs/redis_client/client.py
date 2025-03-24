import redis

class RedisClient:
    _client = None

    @classmethod
    def get_client(cls, host, port, db, decode_responses=True):
        if cls._client is None:
            cls._client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True  # Returns string instead of bytes
            )
        return cls._client
