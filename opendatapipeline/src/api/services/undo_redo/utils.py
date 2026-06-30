from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ..data_loads.service import DataLoadService
from ....logger.logger import Logger, logger
import pandas as pd
from bson import ObjectId


mongo_connector = MongoConnector()
mongo_client = mongo_connector.client
session = mongo_client.session
cache_collection = MongoFactory(mongo_client, "cache", session=session)
chats_collection = MongoFactory(mongo_client, "chats", session=session)
files_collection = MongoFactory(mongo_client, "files", session=session)
connection_collection = MongoFactory(mongo_client, "connections", session=session)


def find_source_id(history): # pragma: no cover
    """Finds the source_id from a list of history entries.

    Args:
        history (list): List of history entries where each entry is a dictionary containing `output` and `parameters`.

    Returns:
        str or None: The found source_id, or None if not found.

    Raises:
        Exception: If there is an issue processing the history entries.
    """
    for entry in reversed(history):
        # Check if 'output' has 'source_id'
        if entry['output'] and 'source_id' in entry['output']:
            return entry['output']['source_id']
        
        # If 'output' is None or doesn't have 'source_id', check 'parameters'
        if 'source_id' in entry['parameters']:
            return entry['parameters']['source_id']
    
    # If no 'source_id' is found in the entire history, return None
    return None