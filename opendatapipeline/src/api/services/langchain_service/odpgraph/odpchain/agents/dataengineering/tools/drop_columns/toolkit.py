from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class DropColumnsToolkit(BaseToolkit):
    """
    DropColumns Toolkit.

    This toolkit provides tools for performing operations related to dropping columns from a dataset. 
    It utilizes a data engineering wrapper and user-specific context to create and manage the tools.

    Attributes:
        tools (List[BaseTool]): A list of tools available in the DropColumns toolkit.

    Methods:
        from_aod_api_wrapper(askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
            Creates an instance of the DropColumnsToolkit using the provided DataEngineeringWrapper and context information.
        
        get_tools() -> List[BaseTool]:
            Retrieves the list of tools available in the DropColumns toolkit.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
        """
        Creates an instance of the DropColumnsToolkit using the provided DataEngineeringWrapper and context information.

        Args:
            askondataWrapper (DataEngineeringWrapper): The wrapper used for data engineering operations.
            user_id (str): The unique identifier for the user.
            chat_id (str): The unique identifier for the chat session.
            session (object): The session object used to manage the context.

        Returns:
            BaseToolkit: An instance of DropColumnsToolkit with initialized tools.
        """
        operations: List[Dict] = [
            {
                "mode": "drop_columns",
                "name": "drop_columns",
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
        Retrieves the list of tools available in the DropColumns toolkit.

        Returns:
            List[BaseTool]: A list of tools in the DropColumns toolkit.
        """
        return self.tools