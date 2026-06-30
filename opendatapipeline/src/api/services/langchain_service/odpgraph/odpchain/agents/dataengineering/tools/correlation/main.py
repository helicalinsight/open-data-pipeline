from langchain_classic.agents import AgentType, initialize_agent
from src.configurations.api.config import Config
from langchain_classic.memory import ConversationBufferMemory
from src.core.llm import get_chat_model
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.correlation.toolkit import CorrelationToolkit
from typing import Final
from src.api.services.pyspark_service.utils import Utils
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.base_agent import BaseAgent

CHAT_MEMORY: Final[str] = "chat_memory"


class CorrelationAgent(BaseAgent):
    """Agent for performing correlation operations using a specified language model and data engineering toolkit.

    This agent is initialized with configurations for interacting with the Data Engineering API and managing conversation history.
    
    Attributes:
        model (str): The language model used for generating responses.
        temperature (float): The temperature setting for the language model.
        base_url (str): The base URL for the language model service.
        agent (Agent): An instance of the agent configured for correlation tasks.

    Args:
        user_id (str): The ID of the user.
        chat_id (str): The ID of the chat session.
        session (object): The session object used for data operations.

    Methods:
        agent() -> Agent:
            Returns the configured agent instance.
    """
    def __init__(self, user_id, chat_id, session) -> None:
        super().__init__(user_id, chat_id, session)
        
        self.model = Config().config["langchain"]["model"]
        self.temperature = Config().config["langchain"]["temperature"]
        self.base_url = Config().config["langchain"]["base_url"]
        
        self.history = Utils().load_history("", self.chat.get(CHAT_MEMORY, []))
        self.memory = ConversationBufferMemory(chat_memory=self.history)

        llm = get_chat_model()

        aod = DataEngineeringWrapper()
        toolkit = CorrelationToolkit.from_aod_api_wrapper(aod, user_id, chat_id, session)
        toolkit.get_tools()


        self.agent = initialize_agent(
            toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,handle_parsing_errors=True,max_iterations=1,memory=self.memory
        )
        self.agent.agent.llm_chain.prompt.template=self.agent.agent.llm_chain.prompt.template.replace("... (this Thought/Action/Action Input/Observation can repeat N times)","")
    
    def agent(self):
        """
        Returns the configured agent instance.

        Returns:
            Agent: The agent instance configured for correlation operations.
        """
        return self.agent
