from langchain_classic.agents import AgentType, initialize_agent
from src.configurations.api.config import Config
from langchain_classic.memory import ConversationBufferMemory
from src.core.llm import get_chat_model
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.when_otherwise.toolkit import WhenOtherwiseToolkit
from typing import Final
from src.api.services.pyspark_service.utils import Utils
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.base_agent import BaseAgent

CHAT_MEMORY: Final[str] = "chat_memory"


class WhenOtherwiseAgent(BaseAgent):
    """Agent for handling conditional operations with 'when' and 'otherwise' logic.

    The `WhenOtherwiseAgent` class is designed to facilitate conditional data processing
    using 'when' and 'otherwise' logic. It utilizes the LangChain model and a data engineering
    API wrapper to perform operations based on the provided user and chat context.

    The agent integrates with the LangChain model and utilizes the `WhenOtherwiseToolkit` to
    perform operations. It is configured with the model details and API connection settings
    specified in the configuration.

    :param user_id: Identifier for the user interacting with the agent.
    :type user_id: str
    :param chat_id: Identifier for the chat session.
    :type chat_id: str
    :param session: Session object managing the interaction with the agent.
    :type session: object
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
        toolkit = WhenOtherwiseToolkit.from_aod_api_wrapper(aod,user_id,chat_id, session)
        toolkit.get_tools()


        self.agent = initialize_agent(
            toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,handle_parsing_errors=True,max_iterations=1,max_execution_time=20,memory=self.memory
        )
        self.agent.agent.llm_chain.prompt.template=self.agent.agent.llm_chain.prompt.template.replace("... (this Thought/Action/Action Input/Observation can repeat N times)","")
    
    def agent(self):
        """Retrieve the initialized agent.

        :return: The agent instance configured with the provided tools and LangChain model.
        :rtype: object
        """
        return self.agent
