import os
from src.cache.mongo_cache import MongoCache
from src.cache.redis_cache import RedisCache

# Default cache type if not set in environment variables
DEFAULT_CACHE_TYPE = "mongo"

def get_cache(**kwargs):
    """Factory function to return a cache instance based on environment variable."""
    cache_type = os.getenv("CACHE_TYPE", DEFAULT_CACHE_TYPE).lower()

    if cache_type == "mongo":
        return MongoCache(**kwargs)
    elif cache_type == "redis":
        return RedisCache(**kwargs)
    else:
        raise ValueError(f"Unsupported cache type: {cache_type}")
