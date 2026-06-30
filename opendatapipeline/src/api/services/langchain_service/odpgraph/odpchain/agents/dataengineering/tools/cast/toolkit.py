from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class CastToolkit(BaseToolkit):
    """
    Toolkit for handling casting operations.

    This toolkit is used for managing casting-related actions within the system.

    Attributes:
        tools (List[BaseTool]): List of tools available in the Cast toolkit.

    Methods:
        from_aod_api_wrapper(askondataWrapper: DataEngineeringWrapper, user_id: str, chat_id: str, session: object) -> BaseToolkit:
            Creates an instance of CastToolkit using the provided DataEngineeringWrapper and user details.
        get_tools() -> List[BaseTool]:
            Retrieves the list of tools available in the Cast toolkit.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
        """
        Creates an instance of CastToolkit with tools configured using the provided DataEngineeringWrapper.

        Args:
            askondataWrapper (DataEngineeringWrapper): The wrapper used for interacting with the data engineering API.
            user_id (str): The ID of the user for whom the toolkit is configured.
            chat_id (str): The ID of the chat session.
            session (object): The session object used for database or API operations.

        Returns:
            BaseToolkit: An instance of CastToolkit with tools initialized based on the provided parameters.
        """
        operations: List[Dict] = [
            {
                "mode": "cast",
                "name": "cast",
                "description": get_prompt(chat_id, session),
            },     
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
        """
        Retrieves the list of tools available in the Cast toolkit.

        Returns:
            List[BaseTool]: The list of tools configured in the Cast toolkit.
        """
        return self.tools