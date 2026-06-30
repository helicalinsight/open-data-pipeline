from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
from abc import ABC, abstractmethod


class DatabaseConnector(ABC):
    
    def __init__(self):
        self.DEFAULT_DB_CONNECTOR_MODE: str = "append"
        self.DEFAULT_S3_CONNECTOR_MODE: str = "overwrite"
    
    @abstractmethod
    @Logger.generate
    def connect(self, connection_id):
        pass

    @abstractmethod
    @Logger.generate
    def test_connection(self, configuration, connection):
        pass

    @abstractmethod
    @Logger.generate
    def fetch_data(self, configuration, connection, custom_config=None):
        pass

    @abstractmethod
    @Logger.generate
    def check_database(self, configuration, connection):
        pass
