from src.core.llm import get_chat_model, LLMConfig
from typing import Final
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.base_agent import BaseAgent

CHAT_MEMORY: Final[str] = "chat_memory"

class PyToolAgent(BaseAgent):
    """Tool agent for interacting with a language model (deepseek-coder-v2) for code-related tasks.
    :param user_id: Identifier for the user interacting with the agent.
    :type user_id: str
    :param chat_id: Identifier for the chat session.
    :type chat_id: str
    :param session: Session object managing the interaction with the language model.
    :type session: object
    """
    def __init__(self, user_id, chat_id, session) -> None:
        """Constructor method to initialize the PyToolAgent with the given parameters.

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
        """Returns the BaseChatModel agent instance used for language model interactions.
        :return: The chat model agent instance.
        :rtype: BaseChatModel
        """
        return self.agent