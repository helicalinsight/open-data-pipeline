"""
Base class for the cache layer, this is used to set the interface for the cache layer and is not
expected to be changed too much as the function names would be directly accessed from the code base.
"""

from abc import ABC, abstractmethod


class CacheBase(ABC):
    """
    Abstract class for the cache.
    
    <source_id, user_id, chat_id> is used as the unique key for cache item
    """
    
    @abstractmethod
    def get_item(self, source_id, user_id, chat_id):
        pass
