from langchain_classic.agents import AgentType, initialize_agent
from src.configurations.api.config import Config
from langchain_classic.memory import ConversationBufferMemory
from src.core.llm import get_chat_model
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.filter.toolkit import FilterToolkit
from typing import Final
from src.api.services.pyspark_service.utils import Utils
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.base_agent import BaseAgent

CHAT_MEMORY: Final[str] = "chat_memory"


class FilterAgent(BaseAgent):
    """
    FilterAgent manages the filtering of data based on user specifications.

    This agent initializes with a language model and a toolkit for filtering operations. It uses the `FilterToolkit`
    to handle filtering tasks and is integrated with a language model to process user requests related to data filtering.

    Attributes:
        model (str): The name of the language model used for processing.
        temperature (float): The temperature setting for the language model, controlling randomness in responses.
        base_url (str): The base URL for the language model's API.
        agent (object): The agent instance responsible for performing data filtering operations.

    Methods:
        __init__(self, user_id, chat_id, session) -> None:
            Initializes the `FilterAgent` with the provided user ID, chat ID, and session. Configures the language model
            and initializes the agent for filtering tasks.

        agent(self):
            Returns the agent instance used for performing filtering operations.
    """
    def __init__(self, user_id, chat_id, session) -> None:
        """
        Initializes the `FilterAgent` with the given configuration and sets up the filtering toolkit and agent.

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
        toolkit = FilterToolkit.from_aod_api_wrapper(aod, user_id, chat_id, session)
        toolkit.get_tools()


        self.agent = initialize_agent(
            toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,handle_parsing_errors=True,max_iterations=1,memory=self.memory
        )
        self.agent.agent.llm_chain.prompt.template=self.agent.agent.llm_chain.prompt.template.replace("... (this Thought/Action/Action Input/Observation can repeat N times)","")
    
    def agent(self):
        """
        Returns the agent instance responsible for performing data filtering operations.

        Returns:
            object: The agent instance used for filtering tasks.
        """
        return self.agent
