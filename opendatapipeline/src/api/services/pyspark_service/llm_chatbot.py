from langchain_classic.chains import ConversationChain
from langchain_classic.agents import Tool, initialize_agent, AgentType
from langchain_classic.chains.conversation.memory import ConversationBufferMemory
from src.core.llm import get_chat_model
from pymongo import MongoClient
from langchain_classic.memory import ChatMessageHistory
from .utils import Utils
from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ....models.mongo.mongo_langchain import MongoLangchain
from ....logger.logger import Logger, logger
from typing import Final
import uuid
from datetime import date, datetime, timezone
from langchain_classic.chains import LLMChain
from langchain_core.prompts import PromptTemplate
#from ..langchain_service.odpgraph.odpchain.query_generator import QueryGenerator

CHAT_MEMORY: Final[str] = "chat_memory"
"""
class SQLTool:
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="sql_chat_history", return_messages=True)

    def query(self, input: str):
        logger.info(f"input {input}")
        self.memory.save_context({"input": input}, {"output": "Executed SQL query."})

sql_tool = SQLTool()
"""

class LLMChatBot:
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
            if not chat:
                raise ValueError(f"No chat found for chat_id: {self.chat_id}")
            self.history = Utils().load_history("", chat.get(CHAT_MEMORY, []))
            self.memory = ConversationBufferMemory(chat_memory=self.history)
            logger.info(f"init self.memory {self.memory}")
            self.llm = get_chat_model()
            self.chain = ConversationChain(llm=self.llm, memory=self.memory)
        except Exception as e:
            logger.error(f"Error initializing LLMChatBot: {str(e)}", exc_info=True)
            raise Exception(f"Error initializing LLMChatBot: {str(e)}") from e
        
    def response_chain(self, output):
        logger.info(f"in response_chain!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!: {output}")
        prompt_template = """
        **Task:** Please convert the provided input into markdown format. The output should ensure the explanation is clear and formatted in a readable way and proper code blocks with code snippet, if necessary.

        **Context:** {output}

        **Response:** 
        """
        prompt = PromptTemplate(
            input_variables=["output"],
            template=prompt_template
        )
        logger.info(f"prompt {prompt}")
        response_chain = LLMChain(llm=self.llm, prompt=prompt, memory=self.memory)
        logger.info(f"response_chain {response_chain}")
        reasoning_output = response_chain.run({"output": output})
        logger.info(f"reasoning_output {reasoning_output}")
        return reasoning_output
    
    def invoke_agent(self, input_text):
        try:
            response = self.chain.invoke(input_text)
            logger.info(f"response {response}")
            #output_response = response["response"]
            output_response = self.response_chain(response["response"])
            logger.info(f"output_response {output_response}")
            dt = datetime.now(timezone.utc)
            utc_time = dt.replace(tzinfo=timezone.utc)
            data_to_insert = {
                                "user_id": self.user_id,
                                "chat_id": self.chat_id,
                                "messages":[{"event" : "bot",
                                    "message_id" :str(uuid.uuid4()),
                                    "message": output_response,
                                    "timestamp": utc_time.timestamp() ,
                                    "export":False,
                                    "stage" : "final",
                                    "details":{"refresh":True}}]
                            }
            self.store_response(input_text, output_response)
            return {
                        "success": True,
                        "event": data_to_insert
                    }, 200
        except Exception as e:
            logger.error(f"Error invoking Langchain agent: {str(e)}", exc_info=True)
            return {
                        "success": False,
                        "event": f"Error invoking Langchain agent: {str(e)}"
                    }, 500
        
    def reset_chain(self):
        try:
            self.history = ChatMessageHistory()
            self.history.add_user_message(self.prompt)
            self.history.add_ai_message("")
            mongo_history = Utils().generate_mongo_history(self.history)
            self.mongo_langchain.update_by_chat_id_value(self.chat_id, CHAT_MEMORY, mongo_history)
            logger.info("Reset Successful")
            return {
                        "success": True,
                        "message": "Reset Successful"
                    }, 200
        except Exception as e:
            logger.error(f"Error resetting LLMChatBot: {str(e)}", exc_info=True)
            return {
                        "success": False,
                        "message": f"Error resetting LLMChatBot: {str(e)}"
                    }, 500

    def store_response(self, input, output):
        """
        Store the metadata in the chatbot's memory.
        """
        try:
            # Log the input and output for debugging purposes
            logger.info("Storing response to memory")
            logger.info(f"Input: {input}")
            logger.info(f"Output: {output}")

            logger.info(f"self.memory.buffer {self.memory.buffer}")
            self.memory.save_context({"input": input}, {"output": output})
            logger.info(f"Saved to memory buffer: {self.memory.buffer}")
            
            logger.info(f"self.history {self.history}")
            mongo_history = Utils().generate_mongo_history(self.history)
            status, modified_count = self.mongo_langchain.update_by_chat_id_value(self.chat_id, CHAT_MEMORY, mongo_history)
            logger.info(f"MongoDB update status: {status}, modified count: {modified_count}")
             
        except Exception as e:
            logger.error(f"Error storing response in memory: {str(e)}", exc_info=True)
