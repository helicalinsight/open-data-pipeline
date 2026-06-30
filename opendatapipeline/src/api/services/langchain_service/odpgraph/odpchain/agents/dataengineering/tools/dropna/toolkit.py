from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class DropNaToolkit(BaseToolkit):
    """
    DropNa Toolkit.

    This toolkit is designed for managing operations related to removing NaN (Not a Number) values from datasets. 
    It provides tools to execute the drop NaN operation by interfacing with a data engineering API.

    Attributes:
        tools (List[BaseTool]): A list of tools available in this toolkit.

    Methods:
        from_aod_api_wrapper(askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
            Creates an instance of DropNaToolkit using the provided API wrapper and session details.
        
        get_tools() -> List[BaseTool]:
            Retrieves the tools available in this toolkit.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
        """
        Creates an instance of DropNaToolkit using the provided API wrapper and session details.

        Args:
            askondataWrapper (DataEngineeringWrapper): The API wrapper for data engineering operations.
            user_id (str): The unique identifier for the user.
            chat_id (str): The unique identifier for the chat session.
            session (object): The session object used to manage the context.

        Returns:
            BaseToolkit: An instance of DropNaToolkit with configured tools.
        """
        operations: List[Dict] = [
            {
                "mode": "drop_na",
                "name": "drop_na",
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
        Retrieves the tools available in this toolkit.

        Returns:
            List[BaseTool]: A list of tools available in the DropNaToolkit.
        """
        return self.tools