from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class ExtractToolkit(BaseToolkit):
    """
    Extract Toolkit.

    The ExtractToolkit provides tools for extracting specific data from a dataset based on user-defined criteria.
    It interfaces with the DataEngineeringWrapper to facilitate the extraction process using the provided tools.

    Attributes:
        tools (List[BaseTool]): A list of tools available in the Extract Toolkit.

    Methods:
        from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
            Creates an instance of ExtractToolkit using the provided DataEngineeringWrapper, user ID, chat ID, and session.
            It sets up the necessary tools for data extraction.

        get_tools(self) -> List[BaseTool]:
            Retrieves the list of tools available in the Extract Toolkit.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
        """
        Creates an instance of ExtractToolkit using the provided DataEngineeringWrapper, user ID, chat ID, and session.

        Args:
            askondataWrapper (DataEngineeringWrapper): The wrapper for interfacing with the data engineering API.
            user_id (str): The unique identifier for the user.
            chat_id (str): The unique identifier for the chat session.
            session (object): The session object used to manage the context.

        Returns:
            BaseToolkit: An instance of ExtractToolkit configured with the tools for data extraction.
        """
        operations: List[Dict] = [
            {
                "mode": "extract",
                "name": "extract",
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
        Retrieves the list of tools available in the Extract Toolkit.

        Returns:
            List[BaseTool]: The list of tools in the Extract Toolkit.
        """
        return self.tools
