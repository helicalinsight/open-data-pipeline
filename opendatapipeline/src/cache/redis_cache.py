"""
Cache implementation using Redis backend (Not Implemented yet)
"""
from src.cache.cache_base import CacheBase

from typing import Optional, Any


class RedisCache(CacheBase):
    
    def __init__(self, **kwargs):
        pass
    
    def get_item(self, source_id, user_id, chat_id) -> Optional[Any]:
        raise NotImplementedError()
