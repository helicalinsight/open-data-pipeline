from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class ConcatToolkit(BaseToolkit):
    """Concat Toolkit.

    This toolkit provides tools for performing concatenation operations. It uses the 
    `AskOndataAction` to interact with the Data Engineering API.

    Attributes:
        tools (List[BaseTool]): A list of tools available in the toolkit.

    Methods:
        from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id: str, chat_id: str, session: object) -> BaseToolkit:
            Creates a toolkit instance from the provided API wrapper and user/session details.
        get_tools(self) -> List[BaseTool]:
            Retrieves the tools included in the toolkit.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
        """
        Creates a toolkit instance from the provided API wrapper and user/session details.

        Args:
            askondataWrapper (DataEngineeringWrapper): The API wrapper used for interacting with data engineering services.
            user_id (str): The ID of the user for whom the toolkit is created.
            chat_id (str): The ID of the chat session.
            session (object): The session object used for database or API operations.

        Returns:
            BaseToolkit: An instance of `ConcatToolkit` with tools configured for concatenation operations.
        """
        operations: List[Dict] = [
            {
                "mode": "concat",
                "name": "concat",
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
        Retrieves the tools included in the toolkit.

        Returns:
            List[BaseTool]: A list of tools available in the Concat toolkit.
        """
        return self.tools
