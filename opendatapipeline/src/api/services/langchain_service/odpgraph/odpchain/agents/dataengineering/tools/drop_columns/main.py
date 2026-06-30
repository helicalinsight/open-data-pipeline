from langchain_classic.agents import AgentType, initialize_agent
from src.configurations.api.config import Config
from langchain_classic.memory import ConversationBufferMemory
from src.core.llm import get_chat_model
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.drop_columns.toolkit import DropColumnsToolkit
from typing import Final
from src.api.services.pyspark_service.utils import Utils
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.base_agent import BaseAgent

CHAT_MEMORY: Final[str] = "chat_memory"


class DropColumnsAgent(BaseAgent):
    """
    Drop Columns Agent.

    This agent is responsible for handling operations related to dropping columns from a dataset. 
    It uses a configured language model and a data engineering toolkit to perform these operations. 

    Attributes:
        model (str): The language model used by the agent.
        temperature (float): The temperature setting for the language model.
        base_url (str): The base URL for the language model service.
        agent (Agent): The initialized agent for performing drop column operations.

    Methods:
        __init__(user_id, chat_id, session):
            Initializes the DropColumnsAgent with the given user, chat, and session details. Sets up the language model, data engineering toolkit, and the agent.

        agent() -> Agent:
            Returns the initialized agent.
    """
    def __init__(self, user_id, chat_id, session) -> None:
        """
        Initializes the DropColumnsAgent with the given user, chat, and session details.

        Args:
            user_id (str): The unique identifier for the user.
            chat_id (str): The unique identifier for the chat session.
            session (object): The session object used to manage the context.

        Sets up the language model, data engineering toolkit, and the agent for performing drop column operations.
        """
        super().__init__(user_id, chat_id, session)
        
        self.model = Config().config["langchain"]["model"]
        self.temperature = Config().config["langchain"]["temperature"]
        self.base_url = Config().config["langchain"]["base_url"]
        self.history = Utils().load_history("", self.chat.get(CHAT_MEMORY, []))
        self.memory = ConversationBufferMemory(chat_memory=self.history)
        llm = get_chat_model()

        aod = DataEngineeringWrapper()
        toolkit = DropColumnsToolkit.from_aod_api_wrapper(aod, user_id, chat_id, session)
        toolkit.get_tools()


        self.agent = initialize_agent(
            toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,handle_parsing_errors=True,max_iterations=1,memory=self.memory
        )
        self.agent.agent.llm_chain.prompt.template=self.agent.agent.llm_chain.prompt.template.replace("... (this Thought/Action/Action Input/Observation can repeat N times)","")
    
    def agent(self):
        """
        Returns the initialized agent.

        Returns:
            Agent: The agent configured for drop column operations.
        """
        return self.agent