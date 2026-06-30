from langchain_classic.chains import ConversationChain
from langchain_classic.chains.conversation.memory import ConversationBufferMemory
from src.core.llm import get_chat_model

from pymongo import MongoClient
from langchain_classic.memory import ChatMessageHistory

from .utils import Utils
from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ....logger.logger import Logger, logger
from .prompt import Prompt
from src.api.services.base.service_parent import ServiceParent

class PySparkCodeGenerator(ServiceParent):
    def __init__(self, chat_id, session=None):
        try:
            self.session=session
            self.chat_id= chat_id
            super().__init__(session)
            self.mongo_langchain = MongoFactory(self.client, "langchain", session=self.session)

            self.prompt = Prompt().get_pyspark_code_generation_prompt(self.chat_id, self.session)
            status, chat = self.mongo_langchain.get_by_id_and_value("chat_id", self.chat_id)
            if not chat:
                raise ValueError(f"No chat found for chat_id: {self.chat_id}")
            self.history = Utils().load_history(self.prompt, chat.get("pyspark_bot_memory", []))
            llm = get_chat_model()

            self.chain = ConversationChain(llm=llm, memory=ConversationBufferMemory(chat_memory=self.history))
        except Exception as e:
            logger.error(f"Error initializing PySparkCodeGenerator: {str(e)}", exc_info=True)
            raise Exception(f"Error initializing PySparkCodeGenerator: {str(e)}") from e
            
    def invoke_chain(self, input_text):
        try:
            response = self.chain.invoke(input_text)
            output_response = response["response"]
            code = Utils().extract_code(output_response)
            mongo_history = Utils().generate_mongo_history(self.history)
            self.mongo_langchain.update_by_chat_id_value(self.chat_id, "pyspark_bot_memory", mongo_history)
            logger.info("Pyspark code generated successfully")
            return {
                        "success": True,
                        "code": code,
                        "message": "Pyspark code generated successfully"
                    }, 200
        except Exception as e:
            logger.error(f"Error generation PySpark code: {str(e)}", exc_info=True)
            return {
                        "success": False,
                        "message": f"Error generating PySpark code: {str(e)}"
                    }, 500
        
    def reset_chain(self):
        try:
            self.history = ChatMessageHistory()
            self.history.add_user_message(self.prompt)
            self.history.add_ai_message("")
            mongo_history = Utils().generate_mongo_history(self.history)
            self.mongo_langchain.update_by_chat_id_value(self.chat_id, "pyspark_bot_memory", mongo_history)
            logger.info("Reset Successful")
            return {
                        "success": True,
                        "message": "Reset Successful"
                    }, 200
        except Exception as e:
            logger.error(f"Error resetting PySparkCodeGenerator: {str(e)}", exc_info=True)
            return {
                        "success": False,
                        "message": f"Error resetting PySparkCodeGenerator: {str(e)}"
                    }, 500

