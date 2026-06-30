from langchain_classic.agents import AgentType, initialize_agent
from src.configurations.api.config import Config
from langchain_classic.memory import ConversationBufferMemory
from src.core.llm import get_chat_model
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.aggregations.toolkit import AggregationsToolkit
from typing import Final
from src.api.services.pyspark_service.utils import Utils
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.base_agent import BaseAgent

CHAT_MEMORY: Final[str] = "chat_memory"


class AggregationsAgent(BaseAgent):
    """ 
    Agent for performing data aggregations using language models.

    Attributes:
        model (str): The language model to be used by the agent.
        temperature (float): The temperature setting for the language model.
        base_url (str): The base URL for the language model service.
        agent (Agent): The agent responsible for handling data aggregation tasks.

    Methods:
        agent: Returns the initialized agent for performing data aggregation.
    """
    def __init__(self, user_id, chat_id, session) -> None:
        """
        Initializes the AggregationsAgent with necessary configurations and tools.

        Args:
            user_id (str): The ID of the user interacting with the agent.
            chat_id (str): The ID of the chat session.
            session (object): The session object used for database or API operations.
        
        Initializes the language model, sets up the toolkit, and configures the agent for data aggregation tasks.
        """
        super().__init__(user_id, chat_id, session)
        
        self.model = Config().config["langchain"]["model"]
        self.temperature = Config().config["langchain"]["temperature"]
        self.base_url = Config().config["langchain"]["base_url"]
        
        self.history = Utils().load_history("", self.chat.get(CHAT_MEMORY, []))
        self.memory = ConversationBufferMemory(chat_memory=self.history)

        llm = get_chat_model()

        aod = DataEngineeringWrapper()
        toolkit = AggregationsToolkit.from_aod_api_wrapper(aod, user_id, chat_id, session)
        toolkit.get_tools()


        self.agent = initialize_agent(
            toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,handle_parsing_errors=True,max_iterations=1,memory=self.memory
        )
        self.agent.agent.llm_chain.prompt.template=self.agent.agent.llm_chain.prompt.template.replace("... (this Thought/Action/Action Input/Observation can repeat N times)","")
    
    def agent(self):
        """
        Returns the initialized agent for performing data aggregation.

        Returns:
            Agent: The configured agent for handling data aggregation tasks.
        """
        return self.agent
