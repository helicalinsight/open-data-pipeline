from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class LowerCaseToolkit(BaseToolkit):
    """
    LowerCaseToolkit for managing lowercase transformation operations.

    This toolkit is used to provide tools and configurations for performing lowercase transformations on data. It initializes tools based on an API wrapper and user context.

    Attributes:
        tools (List[BaseTool]): A list of tools available in the LowerCase toolkit.

    Methods:
        from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
            Creates an instance of the LowerCaseToolkit using the provided API wrapper and user context.

        get_tools(self) -> List[BaseTool]:
            Returns the list of tools available in the LowerCase toolkit.
    """
    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper,user_id,chat_id, session) -> BaseToolkit:
        """
        Creates an instance of the LowerCaseToolkit using the provided API wrapper and user context.

        Args:
            askondataWrapper (DataEngineeringWrapper): The API wrapper for data engineering operations.
            user_id (str): The unique identifier for the user.
            chat_id (str): The unique identifier for the chat session.
            session (object): The session object used to manage context.

        Returns:
            BaseToolkit: An instance of LowerCaseToolkit with initialized tools.
        """
        operations: List[Dict] = [
            {
                "mode": "lowercase",
                "name": "lowercase",
                "description": get_prompt(chat_id, session),
            }    
        ]
        tools = [
            AskOndataAction(
                name=action["name"],
                description=action["description"],
                mode=action["mode"],
                user_id=user_id,
                chat_id=chat_id,
                api_wrapper=askondataWrapper,
                session = session
            )
            for action in operations
        ]
        return cls(tools=tools)


    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the LowerCase toolkit."""
        return self.tools
