from langchain_classic.agents import AgentType, initialize_agent
from src.configurations.api.config import Config
from langchain_classic.memory import ConversationBufferMemory
from src.core.llm import get_chat_model
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.fill_na.toolkit import FillNaToolkit
from typing import Final
from src.api.services.pyspark_service.utils import Utils
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.base_agent import BaseAgent

CHAT_MEMORY: Final[str] = "chat_memory"


class FillNaAgent(BaseAgent):
    """
    FillNaAgent is responsible for managing the agent that handles tasks related to filling missing values in data.

    The agent is configured to interact with a data engineering API and use a language model for processing. The agent 
    can handle various operations related to filling missing values in a dataset based on user requests.

    Attributes:
        model (str): The language model used by the agent.
        temperature (float): The temperature setting for the language model.
        base_url (str): The base URL for the language model API.
        agent (Agent): The initialized agent responsible for handling fill missing value operations.

    Args:
        user_id (str): The unique identifier for the user.
        chat_id (str): The unique identifier for the chat session.
        session (object): The session object used to manage the context.

    Methods:
        agent(self):
            Returns the agent instance used for handling fill missing value operations.
    """
    def __init__(self, user_id, chat_id, session) -> None:
        """
        Initializes the FillNaAgent with the necessary configurations and tools.

        Sets up the language model, temperature, and API URL based on the configuration. Initializes the FillNaToolkit
        with the provided DataEngineeringWrapper and configures the agent to handle fill missing value operations.

        Args:
            user_id (str): The unique identifier for the user.
            chat_id (str): The unique identifier for the chat session.
            session (object): The session object used to manage the context.
        """
        super().__init__(user_id, chat_id, session)
        
        self.model = Config().config["langchain"]["model"]
        self.temperature = Config().config["langchain"]["temperature"]
        self.base_url = Config().config["langchain"]["base_url"]
        
        self.history = Utils().load_history("", self.chat.get(CHAT_MEMORY, []))
        self.memory = ConversationBufferMemory(chat_memory=self.history)

        llm = get_chat_model()

        aod = DataEngineeringWrapper()
        toolkit = FillNaToolkit.from_aod_api_wrapper(aod, user_id, chat_id, session)
        toolkit.get_tools()


        self.agent = initialize_agent(
            toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,handle_parsing_errors=True,max_iterations=1,memory=self.memory
        )
        self.agent.agent.llm_chain.prompt.template=self.agent.agent.llm_chain.prompt.template.replace("... (this Thought/Action/Action Input/Observation can repeat N times)","")
    
    def agent(self):
        """
        Returns the agent instance used for handling fill missing value operations.

        Returns:
            Agent: The initialized agent configured for fill missing value tasks.
        """
        return self.agent
