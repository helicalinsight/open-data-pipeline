from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ....logger.logger import Logger, logger
from typing import Final
from .utils import Utils

CHAT_MEMORY: Final[str] = "chat_memory"


class Memory:
    def __init__(self, user_id, chat_id, session=None):
        try:
            logger.info("init")
            self.session=session
            self.user_id=user_id
            self.chat_id= chat_id

            self.mongo_connector = MongoConnector()
            self.mongo_client = self.mongo_connector.client
            self.mongo_langchain = MongoFactory(self.mongo_client, "langchain", session=self.session)
            status, chat = self.mongo_langchain.get_by_id_and_value("chat_id", self.chat_id)

    
    def store_response(self, input, output):
        """
        Store the metadata in the chatbot's memory.
        """
        try:
            logger.info("Storing response to memory")
            logger.info(f"Input: {input}")
            logger.info(f"Output: {output}")

            logger.info(f"self.memory.buffer {self.memory.buffer}")
            self.memory.save_context({"input": input}, {"output": output})
            logger.info(f"Saved to memory buffer: {self.memory.buffer}")
            
            logger.info(f"self.history {self.history}")
            mongo_history = Utils().generate_mongo_history(self.history)
            succ,chat_document=self.chat_collection.get_by_id(self.chat_id)
            status, modified_count = self.mongo_langchain.update_by_chat_id_value(self.chat_id, CHAT_MEMORY, mongo_history)
            logger.info(f"MongoDB update status: {status}, modified count: {modified_count}")
             
        except Exception as e:
            logger.error(f"Error storing response in memory: {str(e)}", exc_info=True)
