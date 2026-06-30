from langchain_classic.agents import AgentExecutor, Tool, initialize_agent, AgentType
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.conversation.memory import ConversationBufferMemory
from src.core.llm import get_chat_model
from langchain_core.tools import tool
from typing import Optional, Dict, Any, Final
from ....logger.logger import Logger, logger
from .utils import Utils

CHAT_MEMORY: Final[str] = "chat_memory"


class RoutingAgent:
    def __init__(self, user_id, chat_id, session=None):
        try:
            logger.info("init")
            self.session=session
            self.user_id=user_id
            self.chat_id= chat_id
            llm = get_chat_model()
            self.agent = llm
        except Exception as e:
            logger.error(f"Error initializing RoutingAgent: {str(e)}", exc_info=True)
            raise Exception(f"Error initializing RoutingAgent: {str(e)}") from e

    def agent(self):
        """Returns the BaseChatModel agent instance used for language model interactions.

        :return: The chat model agent instance.
        :rtype: BaseChatModel
        """
        return self.agent

    def invoke_agent(self, input_text):
        logger.info(f"invoke_agent {input_text}")
        router_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert router for data engineering requests.  
Analyze the user's input and determine which specialist should handle it.
If the input is a greeting or non-relevant statement, do not respond.
Respond ONLY with one of the following exact options:  
- data_ingestion  
- data_transformation  
- data_quality  
- pipeline_orchestration  
- data_modeling
- data_analysis
- greeting
- other_requests

If you are unable to identify, respond with "other_requests"."""),
            ("human", "{input}")
        ])
        #logger.info(f"router_prompt {router_prompt}")
        routing_output = self.agent.invoke(router_prompt.format(input=input_text)).content
        logger.info(f"routing_output {routing_output}")
        return routing_output
