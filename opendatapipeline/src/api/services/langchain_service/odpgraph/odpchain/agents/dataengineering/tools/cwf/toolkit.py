from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import CURRENT_WORKING_FILE_PROMPT
from ...common_tools.actionclass import AskOndataAction



class CurrentWorkingFileToolkit(BaseToolkit):
    """Toolkit for managing and interacting with the current working file.

    This toolkit provides a set of tools for operations related to the current working file context. It initializes the tools based on the provided data engineering API wrapper and configuration.

    Attributes:
        tools (List[BaseTool]): List of tools available in the toolkit.

    Methods:
        from_aod_api_wrapper(askondataWrapper: DataEngineeringWrapper, user_id: str, chat_id: str, session: object) -> BaseToolkit:
            Class method to initialize the toolkit with tools based on the provided API wrapper and configuration.
        
        get_tools() -> List[BaseTool]:
            Returns the list of tools available in the toolkit.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper,user_id,chat_id, session) -> BaseToolkit:
        """
        Initializes the toolkit with tools based on the provided DataEngineeringWrapper and configuration.

        Args:
            askondataWrapper (DataEngineeringWrapper): The API wrapper used for data engineering operations.
            user_id (str): The ID of the user.
            chat_id (str): The ID of the chat session.
            session (object): The session object used for data operations.

        Returns:
            BaseToolkit: An instance of CurrentWorkingFileToolkit initialized with the tools.
        """
        operations: List[Dict] = [
            {
                "mode": "cwf",
                "name": "cwf",
                "description": CURRENT_WORKING_FILE_PROMPT,
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
        Retrieves the list of tools available in the toolkit.

        Returns:
            List[BaseTool]: The list of tools in the toolkit.
        """
        return self.tools