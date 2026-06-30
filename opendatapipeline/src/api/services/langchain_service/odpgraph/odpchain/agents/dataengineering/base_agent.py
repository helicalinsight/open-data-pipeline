from src.models.connector import MongoConnector
from src.models.mongo.mongo_factory import MongoFactory
from src.logger.logger import logger

class BaseAgent:
    def __init__(self, user_id: str, chat_id: str, session: object) -> None:
        self.session = session
        self.user_id = user_id
        self.chat_id = chat_id

        self.mongo_connector = MongoConnector()
        self.mongo_client = self.mongo_connector.client
        self.mongo_langchain = MongoFactory(self.mongo_client, "langchain", session=self.session)

        status, chat = self.mongo_langchain.get_by_id_and_value("chat_id", self.chat_id)
        if not chat:
            raise ValueError(f"No chat found for chat_id: {self.chat_id}")
        self.chat = chat
