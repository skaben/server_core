import redis
from redis import ConnectionPool
from functools import lru_cache
from django.conf import settings

_pool = ConnectionPool(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, password=settings.REDIS_PASSWORD
)


@lru_cache(maxsize=128)
def get_redis_client():
    """
    Returns a Redis client object using the shared connection pool.
    """
    return redis.Redis(connection_pool=_pool)
