import pytest

from src.cache.cache_factory import get_cache
from src.cache.mongo_cache import MongoCache
from src.models.connector import MongoConnector

@pytest.fixture
def mongo_session():
    return MongoConnector().client._Database__client.start_session()


class TestCacheLayer:
    
    def test_initialize_mongo_cache_by_default(self, mongo_session):
        kwargs = {'session': mongo_session}
        cache = get_cache(**kwargs)
        
        assert type(cache) == MongoCache
    