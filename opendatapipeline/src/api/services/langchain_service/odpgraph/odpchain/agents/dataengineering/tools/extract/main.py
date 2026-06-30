from langchain_classic.agents import AgentType, initialize_agent
from src.configurations.api.config import Config
from langchain_classic.memory import ConversationBufferMemory
from src.core.llm import get_chat_model
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.extract.toolkit import ExtractToolkit
from typing import Final
from src.api.services.pyspark_service.utils import Utils
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.base_agent import BaseAgent

CHAT_MEMORY: Final[str] = "chat_memory"


class ExtractAgent(BaseAgent):
    """
    Extract Agent.

    The ExtractAgent is responsible for managing the extraction of specific data based on user input. It initializes
    the necessary components, including the language model and data engineering toolkit, to handle extraction tasks.

    Attributes:
        model (str): The language model used for generating responses.
        temperature (float): The temperature setting for the language model, influencing the randomness of outputs.
        base_url (str): The base URL for the language model API.
        agent (Agent): An instance of the initialized agent configured with tools for data extraction.

    Methods:
        __init__(user_id, chat_id, session) -> None:
            Initializes the ExtractAgent with user, chat, and session information, setting up the necessary components
            for data extraction.
        
        agent() -> Agent:
            Returns the initialized agent responsible for handling extraction tasks.
    """
    def __init__(self, user_id, chat_id, session) -> None:
        """
        Initializes the ExtractAgent with user, chat, and session information.

        Sets up the conversation memory, language model, and data engineering toolkit, and initializes the agent
        configured with tools for data extraction.

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
        toolkit = ExtractToolkit.from_aod_api_wrapper(aod, user_id, chat_id, session)
        toolkit.get_tools()


        self.agent = initialize_agent(
            toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,handle_parsing_errors=True,max_iterations=1,memory=self.memory
        )
        self.agent.agent.llm_chain.prompt.template=self.agent.agent.llm_chain.prompt.template.replace("... (this Thought/Action/Action Input/Observation can repeat N times)","")
    
    def agent(self):
        """
        Returns the initialized agent responsible for handling extraction tasks.

        Returns:
            Agent: The agent configured for data extraction.
        """
        return self.agent
