from langchain_classic.agents import AgentType, initialize_agent
from src.configurations.api.config import Config
from langchain_classic.memory import ConversationBufferMemory
from src.core.llm import get_chat_model
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.lowercase.toolkit import LowerCaseToolkit
from typing import Final
from src.api.services.pyspark_service.utils import Utils
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.base_agent import BaseAgent

CHAT_MEMORY: Final[str] = "chat_memory"


class LowerCaseAgent(BaseAgent):
    """
    LowerCaseAgent for managing lowercase transformation operations.

    This agent uses a language model to perform lowercase transformation on data. It initializes with specific configurations and tools for handling such operations.

    Attributes:
        model (str): The language model used for generating responses.
        temperature (float): The temperature setting for the language model.
        base_url (str): The base URL for the language model API.
        agent (object): The initialized agent used for performing operations.

    Methods:
        __init__(self, user_id, chat_id, session) -> None:
            Initializes the LowerCaseAgent with the provided user, chat, and session information. Sets up the necessary model and tools.

        agent(self):
            Returns the agent instance used for performing lowercase transformation operations.
    """
    def __init__(self,user_id,chat_id, session) -> None:
        """
        Initializes the LowerCaseAgent with the provided user, chat, and session information.

        Args:
            user_id (str): The unique identifier for the user.
            chat_id (str): The unique identifier for the chat session.
            session (object): The session object used to manage context.

        Returns:
            None
        """
        super().__init__(user_id, chat_id, session)
        
        self.model = Config().config["langchain"]["model"]
        self.temperature = Config().config["langchain"]["temperature"]
        self.base_url = Config().config["langchain"]["base_url"]
        self.history = Utils().load_history("", self.chat.get(CHAT_MEMORY, []))
        self.memory = ConversationBufferMemory(chat_memory=self.history)

        llm = get_chat_model()

        aod = DataEngineeringWrapper()
        toolkit = LowerCaseToolkit.from_aod_api_wrapper(aod, user_id, chat_id, session)
        toolkit.get_tools()


        self.agent = initialize_agent(
            toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,handle_parsing_errors=True,max_iterations=1,max_execution_time=20,memory=self.memory
        )
        self.agent.agent.llm_chain.prompt.template=self.agent.agent.llm_chain.prompt.template.replace("... (this Thought/Action/Action Input/Observation can repeat N times)","")
    
    def agent(self):
        """
        Returns the agent instance used for performing lowercase transformation operations.

        Returns:
            object: The agent instance.
        """
        return self.agent
