from src.models.connector import MongoConnector
from src.models.mongo.mongo_factory import MongoFactory
from typing import Final
from src.api.services.pyspark_service.utils import Utils
from src.logger.logger import Logger, logger

CHAT_MEMORY: Final[str] = "chat_memory"


class ContextModel:
    def __init__(self, session=None):
        self.session = session
        self.mongo_connector = MongoConnector()
        self.mongo_client = self.mongo_connector.client
        self.mongo_langchain = MongoFactory(self.mongo_client, "langchain", session=self.session)
        
    def load_context(self, chat_id):
        _, chat = self.mongo_langchain.get_by_id_and_value("chat_id", chat_id)
        history = Utils().load_history("", chat.get(CHAT_MEMORY, []))
        return history
        
    def save_context(self, chat_id, history):
        mongo_history = Utils().generate_mongo_history(history)
        status, modified_count = self.mongo_langchain.update_by_chat_id_value(chat_id, CHAT_MEMORY, mongo_history)
        logger.info(f"MongoDB update status: {status}, modified count: {modified_count}")