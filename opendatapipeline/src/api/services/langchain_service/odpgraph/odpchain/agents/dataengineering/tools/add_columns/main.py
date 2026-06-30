from langchain_classic.agents import AgentType, initialize_agent
from src.configurations.api.config import Config
from langchain_classic.memory import ConversationBufferMemory
from src.core.llm import get_chat_model
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.add_columns.toolkit import AddColumnToolkit
from typing import Final
from src.api.services.pyspark_service.utils import Utils
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.base_agent import BaseAgent

CHAT_MEMORY: Final[str] = "chat_memory"


class AddColumnsAgent(BaseAgent):
    """
    An agent for adding columns to a dataset using a language model and a set of tools.

    Attributes:
        model (str): The model name used for the language model.
        temperature (float): The temperature setting for the language model.
        base_url (str): The base URL for the language model API.
        agent (Agent): The agent instance initialized with the tools and language model.

    Methods:
        agent: Returns the initialized agent instance.
    """
    def __init__(self, user_id, chat_id, session) -> None:
        """
        Initializes the AddColumnsAgent with the specified user ID, chat ID, and session.

        Args:
            user_id (str): The ID of the user interacting with the agent.
            chat_id (str): The ID of the chat session.
            session (object): The session object used for database or API operations.
        """
        super().__init__(user_id, chat_id, session)
        
        self.model = Config().config["langchain"]["model"]
        self.temperature = Config().config["langchain"]["temperature"]
        self.base_url = Config().config["langchain"]["base_url"]
        
        self.history = Utils().load_history("", self.chat.get(CHAT_MEMORY, []))
        self.memory = ConversationBufferMemory(chat_memory=self.history)

        llm = get_chat_model()

        aod = DataEngineeringWrapper()
        toolkit = AddColumnToolkit.from_aod_api_wrapper(aod, user_id, chat_id, session)
        toolkit.get_tools()


        self.agent = initialize_agent(
            toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,handle_parsing_errors=True,max_iterations=1,memory=self.memory
        )
        self.agent.agent.llm_chain.prompt.template=self.agent.agent.llm_chain.prompt.template.replace("... (this Thought/Action/Action Input/Observation can repeat N times)","")
    
    def agent(self):
        """
        Returns the initialized agent instance.

        Returns:
            Agent: The agent instance with the language model and tools.
        """
        return self.agent