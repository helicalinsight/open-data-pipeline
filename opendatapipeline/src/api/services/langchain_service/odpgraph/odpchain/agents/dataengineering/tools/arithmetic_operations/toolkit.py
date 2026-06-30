from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class  ArithmeticOperationsToolkit(BaseToolkit):
    """
    Toolkit for handling arithmetic operations.

    Inherits from:
        BaseToolkit: Base class for all toolkits.

    Attributes:
        tools (List[BaseTool]): List of tools available in the ArithmeticOperationsToolkit.

    Methods:
        from_aod_api_wrapper: Creates an instance of ArithmeticOperationsToolkit from a DataEngineeringWrapper.
        get_tools: Returns the list of tools in the toolkit.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
        """
        Creates an instance of ArithmeticOperationsToolkit using a DataEngineeringWrapper and configuration details.

        Args:
            askondataWrapper (DataEngineeringWrapper): The wrapper used for API interactions.
            user_id (str): The ID of the user for whom the toolkit is being configured.
            chat_id (str): The ID of the chat session.
            session (object): The session object used for database or API operations.

        Returns:
            BaseToolkit: An instance of ArithmeticOperationsToolkit initialized with tools.

        Notes:
            - This method sets up the toolkit with tools specific to arithmetic operations by creating instances of AskOndataAction.
            - The `get_prompt` function is used to generate descriptions for the tools.
        """
        operations: List[Dict] = [
            {
                "mode": "arithmetic_operations",
                "name": "arithmetic_operations",
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
        Retrieves the list of tools available in the ArithmeticOperations toolkit.

        Returns:
            List[BaseTool]: The list of tools configured in the toolkit.
        """
        return self.tools
