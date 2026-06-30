from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class FilterToolkit(BaseToolkit):
    """
    Filter Toolkit for managing filtering operations.

    This toolkit provides the tools necessary for filtering data based on user-defined criteria. It utilizes the 
    `AskOndataAction` to perform filtering tasks through the `DataEngineeringWrapper` API.

    Attributes:
        tools (List[BaseTool]): A list of tools available in the toolkit for performing filtering operations.

    Methods:
        from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
            Creates a `FilterToolkit` instance from the provided API wrapper and user session information.

        get_tools(self) -> List[BaseTool]:
            Returns the list of tools available in the toolkit.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
        """
        Creates a `FilterToolkit` instance with tools for filtering data.

        Args:
            askondataWrapper (DataEngineeringWrapper): The API wrapper for data engineering operations.
            user_id (str): The unique identifier for the user.
            chat_id (str): The unique identifier for the chat session.
            session (object): The session object used to manage context.

        Returns:
            BaseToolkit: An instance of `FilterToolkit` with the appropriate tools for filtering.
        """
        operations: List[Dict] = [
            {
                "mode": "filter",
                "name": "filter",
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
        """
        Retrieves the tools available in the `FilterToolkit`.

        Returns:
            List[BaseTool]: A list of tools used for filtering data.
        """
        return self.tools
