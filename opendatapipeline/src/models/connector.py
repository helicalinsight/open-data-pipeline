# mongo_utils.py

from core.mongo.connector import MongoConnector as CoreMongoConnector

class MongoConnector(CoreMongoConnector):
    """
    Thread-safe singleton class to handle the connection to a MongoDB instance.
    Inherits from CoreMongoConnector.
    """
    pass
