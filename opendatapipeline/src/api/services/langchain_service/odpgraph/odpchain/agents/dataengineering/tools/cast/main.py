from langchain_classic.agents import AgentType, initialize_agent
from src.configurations.api.config import Config
from langchain_classic.memory import ConversationBufferMemory
from src.core.llm import get_chat_model
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.cast.toolkit import CastToolkit
from typing import Final
from src.api.services.pyspark_service.utils import Utils
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.base_agent import BaseAgent

CHAT_MEMORY: Final[str] = "chat_memory"


class CastAgent(BaseAgent):
    """
    Agent for handling casting operations.

    This agent is designed to use the `Ollama` model and integrate with the `CastToolkit` for casting-related tasks.

    Attributes:
        model (str): The model name retrieved from the configuration.
        temperature (float): The temperature setting for the model, retrieved from the configuration.
        base_url (str): The base URL for the model, retrieved from the configuration.
        agent (Agent): The initialized agent for performing casting operations.

    Methods:
        __init__(user_id, chat_id, session):
            Initializes the CastAgent with the given user, chat, and session details.
        agent():
            Returns the initialized agent for casting operations.
    """
    def __init__(self, user_id, chat_id, session) -> None:
        """
        Initializes the CastAgent with the specified user ID, chat ID, and session.

        Args:
            user_id (str): The ID of the user for whom the agent is configured.
            chat_id (str): The ID of the chat session.
            session (object): The session object used for database or API operations.

        Notes:
            - The constructor sets up the `Ollama` model with configuration details.
            - Initializes the `CastToolkit` using `DataEngineeringWrapper` and configuration parameters.
            - Configures the agent with the toolkit's tools and sets up the prompt template.
        """
        super().__init__(user_id, chat_id, session)
        
        self.model = Config().config["langchain"]["model"]
        self.temperature = Config().config["langchain"]["temperature"]
        self.base_url = Config().config["langchain"]["base_url"]
        
        self.history = Utils().load_history("", self.chat.get(CHAT_MEMORY, []))
        self.memory = ConversationBufferMemory(chat_memory=self.history)

        llm = get_chat_model()

        aod = DataEngineeringWrapper()
        toolkit = CastToolkit.from_aod_api_wrapper(aod, user_id, chat_id, session)
        toolkit.get_tools()


        self.agent = initialize_agent(
            toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,handle_parsing_errors=True,max_iterations=1,memory=self.memory
        )
        self.agent.agent.llm_chain.prompt.template=self.agent.agent.llm_chain.prompt.template.replace("... (this Thought/Action/Action Input/Observation can repeat N times)","")
    
    def agent(self):
        """
        Returns the initialized agent for casting operations.

        Returns:
            Agent: The agent configured for casting tasks.
        """
        return self.agent