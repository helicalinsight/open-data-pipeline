"""
Cache implementation using Mongo backend
"""
from src.cache.cache_base import CacheBase
from src.models.mongo.mongo_factory import MongoFactory
from src.models.connector import MongoConnector

from typing import Optional, Any


class MongoCache(CacheBase):
    
    def __init__(self, **kwargs):
        if 'session' not in kwargs:
            raise RuntimeError("`session` object is required to initialize mongo cache")
        
        self.session = kwargs['session']
        self.mongo_connector = MongoConnector()
        self.mongo_client = self.mongo_connector.client
        self.mongo_cache = MongoFactory(self.mongo_client, "cache", session=self.session)
    
    def get_item(self, source_id, user_id, chat_id) -> Optional[Any]:
        if source_id is None or user_id is None or chat_id is None:
            raise ValueError("Cache get item received invalid values. Expected non-null values for key, received - ")
        success, item = self.mongo_cache.get_by_fields(source_id, user_id, chat_id)
        
        if not success:
            return None
        
        return item
    