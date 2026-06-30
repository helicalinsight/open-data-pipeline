from dlt_server.models.connector import MongoConnector
from core.mongo.mongo_factory import MongoFactory

from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *

mongo_connector = MongoConnector()
mongo_client = mongo_connector.client
mongo_schedule = MongoFactory(mongo_client, "schedule")
logger = Logger


class Configuration:
    @logger.generate
    def get(self, schedule_id):
        try:
            success, chat = mongo_schedule.get_by_id(schedule_id)
            if not success or chat is None:
                logger.debug("Chat history not found.")
                raise Exception
            configuration = chat.get('configurations', {})
            return configuration
        except Exception as e:
            logger.error(f"Error getting configuration: Failed to get configuration with schedule_id :{schedule_id}")
            raise UtilsException("Failed to get configuration.") from e
