from langchain_classic.agents import AgentType, initialize_agent
from src.core.llm import get_chat_model, LLMConfig
from typing import Final
from src.api.services.pyspark_service.utils import Utils
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.base_agent import BaseAgent

CHAT_MEMORY: Final[str] = "chat_memory"


class SaprkToolAgent(BaseAgent):
    """An agent for interacting with a language model specifically configured for Spark-related tasks.

    This class initializes a language model using configuration settings from `LangchainConfig`. It sets up
    the model and temperature parameters to interact with Spark-related tasks.

    :param user_id: Identifier for the user interacting with the agent.
    :type user_id: str
    :param chat_id: Identifier for the chat session.
    :type chat_id: str
    :param session: Session object managing the interaction with the language model.
    :type session: object
    """
    def __init__(self,user_id,chat_id, session) -> None:
        """Constructor method to initialize the SaprkToolAgent with the given parameters and configure
        the language model for Spark-related tasks.

        :param user_id: Identifier for the user interacting with the agent.
        :type user_id: str
        :param chat_id: Identifier for the chat session.
        :type chat_id: str
        :param session: Session object managing the interaction with the language model.
        :type session: object
        """
        super().__init__(user_id, chat_id, session)
        
        self.agent = get_chat_model(LLMConfig.from_env_and_config(extra={"cache": False}))

    def agent(self):
        """Returns the initialized language model agent.

        :return: The language model instance configured for Spark-related tasks.
        :rtype: BaseChatModel
        """
        return self.agent
