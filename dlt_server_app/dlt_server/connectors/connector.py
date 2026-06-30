
from core.mongo.connector import MongoConnector as CoreMongoConnector
from dlt_server.configurations.mongo.config import MongoConfig

class MongoConnector(CoreMongoConnector):
    """
    Thread-safe singleton class to handle the connection to a MongoDB instance for DLT Engine.
    Inherits from CoreMongoConnector.
    """
    
    def _get_config(self):
        """
        Retrieve configuration for dlt server.
        """
        return MongoConfig.config

