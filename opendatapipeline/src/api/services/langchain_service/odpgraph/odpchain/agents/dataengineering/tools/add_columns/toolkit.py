from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction




class AddColumnToolkit(BaseToolkit):
    """
    Toolkit for adding columns to a dataset.

    Inherits:
        BaseToolkit: The base class for toolkits.

    Attributes:
        tools (List[BaseTool]): A list of tools available in the toolkit.

    Methods:
        from_aod_api_wrapper: Creates an instance of AddColumnToolkit from a DataEngineeringWrapper.
        get_tools: Returns the list of tools in the toolkit.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper,user_id,chat_id, session) -> BaseToolkit:
        """
        Creates an instance of AddColumnToolkit from a DataEngineeringWrapper and other parameters.

        Args:
            askondataWrapper (DataEngineeringWrapper): The wrapper for data engineering operations.
            user_id (str): The ID of the user interacting with the toolkit.
            chat_id (str): The ID of the chat session.
            session (object): The session object used for database or API operations.

        Returns:
            BaseToolkit: An instance of AddColumnToolkit with the initialized tools.
        """
        operations: List[Dict] = [
            {
                "mode": "add_columns",
                "name": "add_columns",
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
        Returns the list of tools available in the toolkit.

        Returns:
            List[BaseTool]: A list of tools in the toolkit.
        """
        return self.tools