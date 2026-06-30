from langchain_classic.agents import AgentType, initialize_agent
from src.configurations.api.config import Config
from langchain_classic.memory import ConversationBufferMemory
from src.core.llm import get_chat_model
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.rearrange_columns.toolkit import RearrangeColumnsToolkit
from typing import Final
from src.api.services.pyspark_service.utils import Utils
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.base_agent import BaseAgent

CHAT_MEMORY: Final[str] = "chat_memory"


class RearrangeColumnsAgent(BaseAgent):
    """This class represents an agent for rearranging columns in data using a language model. It utilizes
    configuration from a `Config` class, integrates with an `Ollama` language model, and utilizes tools
    from a `DataEngineeringWrapper` for its operations.

    :param user_id: Identifier for the user interacting with the agent.
    :type user_id: str
    :param chat_id: Identifier for the chat session.
    :type chat_id: str
    :param session: Session object managing the interaction with the language model.
    :type session: object
    """
    def __init__(self,user_id,chat_id, session) -> None:
        """Constructor method to initialize the RearrangeColumnsAgent with the given parameters and set up
        the language model and tools for column rearrangement.

        :param user_id: Identifier for the user interacting with the agent.
        :type user_id: str
        :param chat_id: Identifier for the chat session.
        :type chat_id: str
        :param session: Session object managing the interaction with the language model.
        :type session: object
        """
        super().__init__(user_id, chat_id, session)
        
        self.model = Config().config["langchain"]["model"]
        self.temperature = Config().config["langchain"]["temperature"]
        self.base_url = Config().config["langchain"]["base_url"]
        
        self.history = Utils().load_history("", self.chat.get(CHAT_MEMORY, []))
        self.memory = ConversationBufferMemory(chat_memory=self.history)
        llm = get_chat_model()
        aod = DataEngineeringWrapper()
        toolkit = RearrangeColumnsToolkit.from_aod_api_wrapper(aod,user_id,chat_id, session)
        toolkit.get_tools()


        self.agent = initialize_agent(
            toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,handle_parsing_errors=True,max_iterations=1,memory=self.memory
        )
        self.agent.agent.llm_chain.prompt.template=self.agent.agent.llm_chain.prompt.template.replace("... (this Thought/Action/Action Input/Observation can repeat N times)","")
    
    def agent(self):
        """Returns the initialized agent for rearranging columns.

        :return: The agent instance used for column rearrangement tasks.
        :rtype: Agent
        """
        return self.agent
