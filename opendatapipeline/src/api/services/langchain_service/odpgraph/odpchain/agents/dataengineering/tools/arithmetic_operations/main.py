from langchain_classic.agents import AgentType, initialize_agent
from src.configurations.api.config import Config
from langchain_classic.memory import ConversationBufferMemory
from src.core.llm import get_chat_model
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.arithmetic_operations.toolkit import ArithmeticOperationsToolkit
from typing import Final
from src.api.services.pyspark_service.utils import Utils
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.base_agent import BaseAgent

CHAT_MEMORY: Final[str] = "chat_memory"


class ArithmeticOperationsAgent(BaseAgent):
    """
    Agent for handling arithmetic operations using a language model and a toolkit.

    Attributes:
        model (str): The model used by the language model.
        temperature (float): The temperature setting for the language model.
        base_url (str): The base URL for the language model service.
        agent (Agent): The initialized agent for performing arithmetic operations.

    Methods:
        __init__: Initializes the ArithmeticOperationsAgent with configuration details and sets up the agent.
        agent: Returns the agent instance configured for arithmetic operations.
    """
    def __init__(self, user_id, chat_id, session) -> None:
        """
        Initializes the ArithmeticOperationsAgent with configuration details and sets up the agent.

        Args:
            user_id (str): The ID of the user for whom the agent is being configured.
            chat_id (str): The ID of the chat session.
            session (object): The session object used for database or API operations.

        Notes:
            - This method configures the language model and initializes the agent for arithmetic operations.
            - Sets up conversation memory and configures the toolkit and agent using the provided user and chat information.
        """
        super().__init__(user_id, chat_id, session)
        
        self.model = Config().config["langchain"]["model"]
        self.temperature = Config().config["langchain"]["temperature"]
        self.base_url = Config().config["langchain"]["base_url"]
        
        self.history = Utils().load_history("", self.chat.get(CHAT_MEMORY, []))
        self.memory = ConversationBufferMemory(chat_memory=self.history)

        llm = get_chat_model()

        aod = DataEngineeringWrapper()
        toolkit = ArithmeticOperationsToolkit.from_aod_api_wrapper(aod, user_id, chat_id, session)
        toolkit.get_tools()


        self.agent = initialize_agent(
            toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,handle_parsing_errors=True,max_iterations=1,memory=self.memory
        )
        self.agent.agent.llm_chain.prompt.template=self.agent.agent.llm_chain.prompt.template.replace("... (this Thought/Action/Action Input/Observation can repeat N times)","")
    
    def agent(self):
        """
        Returns the agent instance configured for arithmetic operations.

        Returns:
            Agent: The initialized agent for performing arithmetic operations.
        """
        return self.agent
