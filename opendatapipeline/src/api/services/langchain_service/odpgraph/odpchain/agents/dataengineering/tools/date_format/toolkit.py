from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class DateFormatToolkit(BaseToolkit):
    """
    DateFormat Toolkit for managing date format operations.

    This toolkit provides tools for handling date format tasks through interactions with a data engineering API. 
    It initializes tools based on the operations defined for date formatting.

    Attributes:
        tools (List[BaseTool]): A list of tools available in the toolkit.

    Methods:
        from_aod_api_wrapper(askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
            Creates an instance of the toolkit from an API wrapper and user/session information.

        get_tools() -> List[BaseTool]:
            Retrieves the list of tools available in the DateFormat toolkit.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
        """
        Creates an instance of the DateFormatToolkit from an API wrapper.

        Args:
            askondataWrapper (DataEngineeringWrapper): The API wrapper for interacting with the data engineering service.
            user_id (str): The ID of the user.
            chat_id (str): The ID of the chat session.
            session (object): The session object used for querying data.

        Returns:
            BaseToolkit: An instance of DateFormatToolkit configured with the tools for date format operations.
        """
        operations: List[Dict] = [
            {
                "mode": "date_format",
                "name": "date_format",
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
                session=session
            )
            for action in operations
        ]
        return cls(tools=tools)


    def get_tools(self) -> List[BaseTool]:
        """
        Retrieves the list of tools available in the DateFormat toolkit.

        Returns:
            List[BaseTool]: The list of tools configured in the toolkit.
        """
        return self.tools
