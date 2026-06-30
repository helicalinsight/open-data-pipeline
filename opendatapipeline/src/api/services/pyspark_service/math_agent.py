from langchain_classic.agents import AgentExecutor, Tool, initialize_agent, AgentType, create_react_agent
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.conversation.memory import ConversationBufferMemory
from src.core.llm import get_chat_model, LLMConfig
from langchain_core.tools import tool, StructuredTool
from typing import Optional, Dict, Any
from ....logger.logger import Logger, logger

from ..langchain_service.utils import LangchainServiceUtils
from ....models.mongo.mongo_langchain import MongoLangchain
from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from langchain_classic.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import json
from typing import Final, TypedDict
import uuid
from .utils import Utils
from datetime import date, datetime, timezone
from ..langchain_service.odpgraph.odpchain.agents.memory.memory import Memory
from ..langchain_service.odpgraph.odpchain.agents.context.context import Context
#from langgraph.graph import StateGraph, START, MessagesState, END
from pydantic import BaseModel


CHAT_MEMORY: Final[str] = "chat_memory"

class MathInput(BaseModel):
    a: float
    b: float


class MathAgent:
    def __init__(self, user_id, chat_id, session=None):
        try:
            logger.info("init")
            self.session=session
            self.user_id=user_id
            self.chat_id= chat_id
            
            self.chat_collection = MongoFactory(MongoConnector().client, "chats", self.session)
            self.llm = get_chat_model(LLMConfig(model="deepseek-r1:7b"))
            self.context = Context(self.session)
            self.llm_memory = Memory(self.session)
            self.history = self.llm_memory.load_memory(self.chat_id)
            self.memory = ConversationBufferMemory(chat_memory=self.history)
        except Exception as e:
            logger.error(f"Error initializing DataAnalystAgent: {str(e)}", exc_info=True)
            raise Exception(f"Error initializing DataAnalystAgent: {str(e)}") from e

    @tool(args_schema=MathInput)
    def add(self, a: float, b: float) -> str:
        """Add two numbers."""
        return str(a + b)

    @tool(args_schema=MathInput)
    def multiply(self, a: float, b: float) -> str:
        """Multiply two numbers."""
        return str(a * b)

    @tool(args_schema=MathInput)
    def divide(self, a: float, b: float) -> str:
        """Divide two numbers."""
        return str(a / b)
    
    def process(self, input_task, user_id, chat_id):
        logger.info("in process")  
        tools = [self.add, self.multiply, self.divide]
        logger.info(f"tools {tools}")
        math_agent = create_react_agent(
            llm=self.llm,
            tools=tools,
            prompt=PromptTemplate.from_template("""You are a math agent.
            Answer the following questions as best you can. You have access to the following tools:

            {tools}

            Use the following format:

            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of [{tool_names}]
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question

            Begin!

            Question: {input}
            Thought:{agent_scratchpad}"""
                )
            )
        logger.info(f"math_agent {math_agent}")
        agent_executor = AgentExecutor(agent=math_agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations = 5)
        logger.info(f"agent_executor {agent_executor}")
        try:
            response = agent_executor.invoke({"input": input_task})
            logger.info(f"response {response}")
        except Exception as e:
            logger.error(f"Error in math agent executor invoke: {str(e)}", exc_info=True)
        return response
