from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class DropAllExceptColumnsToolkit(BaseToolkit):
    """
    Drop All Except Columns Toolkit.

    This toolkit provides tools for dropping all columns in a dataset except for the specified columns. 
    It uses an API wrapper to interact with data engineering services and creates tools based on the provided configurations.

    Attributes:
        tools (List[BaseTool]): A list of tools available in the toolkit.

    Methods:
        from_aod_api_wrapper(askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
            Creates an instance of the toolkit from the given API wrapper, user, chat, and session details.
        
        get_tools() -> List[BaseTool]:
            Returns a list of tools available in the toolkit.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
        """
        Creates an instance of the toolkit from the given API wrapper, user, chat, and session details.

        Args:
            askondataWrapper (DataEngineeringWrapper): The API wrapper used for data engineering operations.
            user_id (str): The unique identifier for the user.
            chat_id (str): The unique identifier for the chat session.
            session (object): The session object used to manage the context.

        Returns:
            BaseToolkit: An instance of the DropAllExceptColumnsToolkit with tools configured.
        """
        operations: List[Dict] = [
            {
                "mode": "drop_all_except_columns",
                "name": "drop_all_except_columns",
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
                session=session
            )
            for action in operations
        ]
        return cls(tools=tools)


    def get_tools(self) -> List[BaseTool]:
        """
        Returns a list of tools available in the toolkit.

        Returns:
            List[BaseTool]: A list of tools configured in the DropAllExceptColumnsToolkit.
        """
        return self.tools