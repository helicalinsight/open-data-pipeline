
import uuid
from bson import ObjectId
import os

from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError

from src.api.services.base.service_parent import ServiceParent

from ...exceptions.exception import MongoException
from ...logger.logger import Logger, logger

from core.mongo.mongo_factory import MongoFactory as CoreMongoFactory

class MongoFactory(CoreMongoFactory):
    """
    Factory class for interacting with MongoDB collections.
    
    This class inherits from the core MongoFactory to use the centralized implementation
    while preserving the environment-specific database selection logic required by opendatapipeline.
    """
    def __init__(self, mongo, collection_name, session):
        """
        Initialize the MongoFactory with MongoDB connection, collection name, and session.

        Args:
            mongo (MongoClient): The MongoDB client instance (ignored if session is None, used if valid db object).
            collection_name (str): The name of the collection to interact with.
            session (ClientSession): The MongoDB session instance.
        """
        database = None
        try:
            # Handle session case
            if session is not None:
                # KEEP ORIGINAL LOGIC: Transaction mode with session
                if os.environ.get("APP_ENVIRONMENT") == "dev":
                    database = session.client.user_sessions
                elif os.environ.get("APP_ENVIRONMENT") == "prod":
                    database = session.client.user_sessions
                else:
                    database = session.client.user_sessions_test
                    
                logger.debug("MongoFactory: Using session.client (transaction mode)")
                
            else:
                # Read mode optimization using ServiceParent logic
                logger.debug("MongoFactory: Using ServiceParent ReadConnector optimization")
                
                # Import and use ServiceParent for read optimization
                service_parent = ServiceParent(session=None)
                optimized_client = service_parent.client
                
                # Get correct database using ReadConnector - inline logic
                mongo_client = optimized_client._Database__client
                if os.environ.get("APP_ENVIRONMENT") == "dev":
                    database = mongo_client.user_sessions
                elif os.environ.get("APP_ENVIRONMENT") == "prod":
                    database = mongo_client.user_sessions
                else:
                    database = mongo_client.user_sessions_test
                
                logger.debug("MongoFactory: Using ReadConnector (primaryPreferred)")
            
            # Initialize core factory with the resolved database
            # We pass the local logger to the core factory so it logs using the correct instance
            super().__init__(mongo=database, collection_name=collection_name, session=session, logger=logger)
            
        except Exception as e:
            logger.error(f"MongoFactory initialization failed: {e}", exc_info=True)
            raise MongoException(f"Failed to initialize MongoFactory: {e}")
