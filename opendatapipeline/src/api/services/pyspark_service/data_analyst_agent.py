from langchain_classic.agents import AgentExecutor, Tool, initialize_agent, AgentType
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.conversation.memory import ConversationBufferMemory
from src.core.llm import get_chat_model
from langchain_core.tools import tool
from typing import Optional, Dict, Any
from ....logger.logger import Logger, logger
from ..langchain_service.utils import LangchainServiceUtils
from ....models.mongo.mongo_langchain import MongoLangchain
from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from langchain_classic.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import json
from typing import Final
import uuid
from .utils import Utils
from datetime import date, datetime, timezone
from ..langchain_service.odpgraph.odpchain.agents.dataengineering.tools.sql_operations.toolkit import SQLOperationsToolkit
from ..langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from ..langchain_service.odpgraph.odpchain.agents.memory.memory import Memory
CHAT_MEMORY: Final[str] = "chat_memory"


class DataAnalystAgent:
    def __init__(self, user_id, chat_id, session=None):
        try:
            logger.info("init")
            self.session=session
            self.user_id=user_id
            self.chat_id= chat_id
            
            self.chat_collection = MongoFactory(MongoConnector().client, "chats", self.session)
            self.llm = get_chat_model()
            # Data analysis reasoning tool
            data_analysis_reasoning_tool = Tool.from_function(
                name="Data Analysis Reasoning Tool",
                func=self.data_analysis_reasoning_tool,
                description="Useful for answering data analysis-related logic questions, such as interpreting data, making calculations, or drawing conclusions."
            )
            aod = DataEngineeringWrapper()
            toolkit = SQLOperationsToolkit.from_aod_api_wrapper(aod,user_id,chat_id,session)
            self.tools = toolkit.get_tools()  # Assuming toolkit is a list of Tool objects
            
            #data_analysis_reasoning_tool = self.data_analysis_reasoning_tool()
            self.tools.append(data_analysis_reasoning_tool)
            self.llm_memory = Memory(self.session)
            self.history = self.llm_memory.load_memory(self.chat_id)
            self.memory = ConversationBufferMemory(chat_memory=self.history)
            self.agent = initialize_agent(self.tools, llm, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, memory=self.memory, handle_parsing_errors=True, max_iterations=10,max_execution_time=20)
        except Exception as e:
            logger.error(f"Error initializing DataAnalystAgent: {str(e)}", exc_info=True)
            raise Exception(f"Error initializing DataAnalystAgent: {str(e)}") from e

    def data_analysis_reasoning_tool(self, question:str):
        """
        This function creates the data analysis reasoning tool.
        """
        logger.info(f"in data_analysis_reasoning_tool {question}")
        data_analysis_reasoning_template = """
        You are a data analyst reasoning agent tasked with solving the user's data-related questions. 
        Logically analyze the data-related problem, explain any necessary calculations, and provide factual conclusions.
        In your answers, clearly detail the steps involved, show any necessary calculations, and give the final answer.
        Provide the response in bullet points.

        Question: {question} 

        Answer:
        """
        data_analysis_assistant_prompt = PromptTemplate(
            input_variables=["question"],
            template=data_analysis_reasoning_template
        )

        # Chain for data analysis reasoning tool
        data_analysis_chain = LLMChain(llm=self.llm, prompt=data_analysis_assistant_prompt, verbose=True, memory=self.memory)
        reasoning_output = data_analysis_chain.run(question=question)
        return reasoning_output

    def agent(self):
        """Returns the BaseChatModel instance used for language model interactions.

        :return: The chat model instance.
        :rtype: BaseChatModel
        """
        return self.llm

    def invoke_agent(self, input_text):
        logger.info(f"invoke_agent {input_text}")
        langchain_utils = LangchainServiceUtils(self.session, self.llm)
        resp=langchain_utils.sql_generator(input_text,self.chat_id)
        logger.info(f"resp {resp}")
        task=langchain_utils.regex_matcher(resp)
        logger.info(f"task {task}")
        sql_output = self.agent.invoke(task)['output']
        logger.info(f"sql_output {sql_output}")
        dt = datetime.now(timezone.utc)
        utc_time = dt.replace(tzinfo=timezone.utc)
        data_to_insert = {
                            "user_id": self.user_id,
                            "chat_id": self.chat_id,
                            "messages":[{"event" : "bot",
                                "message_id" :str(uuid.uuid4()),
                                "message": sql_output,
                                "timestamp": utc_time.timestamp() ,
                                "export":False,
                                "stage" : "final",
                                "details":{"refresh":True}}]
                        }
        self.llm_memory.update(input_text, sql_output, self.memory, self.history, self.chat_id)
        #self.store_response(input_text, sql_output)
        MongoLangchain(MongoConnector().client, "langchain", self.session).create_or_update(data = data_to_insert)
        self.chat_collection.update_one(self.chat_id, "isChatMode", True )
        return {
                    "success": True,
                    "event": data_to_insert
                }, 200

"""
    def store_response(self, input, output):
        #Store the metadata in the chatbot's memory.
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
            succ,chat_document=self.chat_collection.get_by_id(self.chat_id)
            status, modified_count = self.mongo_langchain.update_by_chat_id_value(self.chat_id, CHAT_MEMORY, mongo_history)
            logger.info(f"MongoDB update status: {status}, modified count: {modified_count}")
             
        except Exception as e:
            logger.error(f"Error storing response in memory: {str(e)}", exc_info=True)
"""