"""
Parent class for all service classes providing conditional MongoDB connector initialization.
"""

import logging
from core.mongo.connector import MongoConnector
from core.mongo.read_connector import ReadMongoConnector
from src.logger.logger import Logger, logger

class ServiceParent:
    """
    Parent class for all service classes.
    Handles MongoDB connector initialization based on session parameter.
    """
    
    def __init__(self, session=None):
        """
        Initialize service with appropriate MongoDB connector.
        
        :param session: Optional MongoDB session for transaction operations
        :type session: pymongo.ClientSession or None
        """
        if session is None:
            # Initialize read connector and client (primaryPreferred)
            self.session = None
            self.client = ReadMongoConnector().client
            logger.info(f"{self.__class__.__name__} initialized with ReadMongoConnector (primaryPreferred)")
        else:
            # Initialize write connector and client (primary)
            self.session = session
            self.client = MongoConnector().client
            logger.info(f"{self.__class__.__name__} initialized with MongoConnector (primary) with session")
    
    def _safe_abort_transaction(self):
        """
        Safely abort transaction only if session exists.
        
        This method prevents errors when called from read-only operations
        by checking if a session exists before attempting to abort the transaction.
        """
        try:
            if self.session is not None:
                self.session.abort_transaction()
                logger.debug(f"{self.__class__.__name__}: Transaction aborted successfully")
            else:
                logger.debug(f"{self.__class__.__name__}: No transaction to abort (session is None)")
                
        except Exception as abort_error:
            logger.warning(f"{self.__class__.__name__}: Error aborting transaction: {abort_error}")
    