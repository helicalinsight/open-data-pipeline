from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import JOIN_FILES_PROMPT
from ...common_tools.actionclass import AskOndataAction



class JoinsToolkit(BaseToolkit):
    """
    JoinsToolkit for managing data join operations.

    This toolkit provides tools to perform data join operations. It initializes tools using the provided API wrapper, user, chat, and session information. 

    Attributes:
        tools (List[BaseTool]): A list of tools available in the JoinsToolkit.

    Methods:
        from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
            Creates a JoinsToolkit instance from the given API wrapper and user/session information.

        get_tools(self) -> List[BaseTool]:
            Retrieves the list of tools available in the JoinsToolkit.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
        """
        Creates a JoinsToolkit instance from the given API wrapper and user/session information.

        Args:
            askondataWrapper (DataEngineeringWrapper): The API wrapper used to interact with the data engineering service.
            user_id (str): The unique identifier for the user.
            chat_id (str): The unique identifier for the chat session.
            session (object): The session object used to manage context.

        Returns:
            BaseToolkit: An instance of JoinsToolkit initialized with tools.
        """
        operations: List[Dict] = [
            {
                "mode": "joins",
                "name": "joins",
                "description": JOIN_FILES_PROMPT,
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
        Retrieves the list of tools available in the JoinsToolkit.

        Returns:
            List[BaseTool]: The list of tools in the JoinsToolkit.
        """
        return self.tools
