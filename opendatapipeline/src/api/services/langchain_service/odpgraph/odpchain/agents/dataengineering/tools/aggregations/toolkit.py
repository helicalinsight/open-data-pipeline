from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class AggregationsToolkit(BaseToolkit):
    """
    Aggregations Toolkit for managing and providing aggregation tools.

    Inherits from:
        BaseToolkit: Base class for toolkit management.

    Attributes:
        tools (List[BaseTool]): A list of tools available in the toolkit.

    Methods:
        from_aod_api_wrapper: Creates an AggregationsToolkit instance using the provided API wrapper and configuration details.
        get_tools: Retrieves the list of tools available in the toolkit.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
        """
        Creates an instance of AggregationsToolkit using the provided API wrapper and configuration details.

        Args:
            askondataWrapper (DataEngineeringWrapper): The wrapper for API operations related to data engineering.
            user_id (str): The ID of the user for whom the toolkit is being configured.
            chat_id (str): The ID of the chat session.
            session (object): The session object used for database or API operations.

        Returns:
            BaseToolkit: An instance of AggregationsToolkit initialized with tools for aggregation operations.
        """
        operations: List[Dict] = [
            {
                "mode": "aggregations",
                "name": "aggregations",
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
                session =session

            )
            for action in operations
        ]
        return cls(tools=tools)


    def get_tools(self) -> List[BaseTool]:
        """
        Retrieves the list of tools available in the Aggregations toolkit.

        Returns:
            List[BaseTool]: A list of tools configured in the toolkit.
        """
        return self.tools
