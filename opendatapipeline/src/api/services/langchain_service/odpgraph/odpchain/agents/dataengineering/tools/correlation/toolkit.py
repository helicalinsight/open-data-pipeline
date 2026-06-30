from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class CorrelationToolkit(BaseToolkit):
    """Toolkit for performing correlation operations.

    This toolkit contains tools for performing correlation tasks using a specified data engineering API wrapper.
    
    Attributes:
        tools (List[BaseTool]): A list of tools available in the toolkit.

    Methods:
        from_aod_api_wrapper(
            askondataWrapper: DataEngineeringWrapper, 
            user_id: str, 
            chat_id: str, 
            session: object
        ) -> BaseToolkit:
            Creates an instance of the toolkit from the provided DataEngineeringWrapper and context.
        
        get_tools() -> List[BaseTool]:
            Returns the list of tools in the toolkit.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
        """
        Creates an instance of the CorrelationToolkit from the provided DataEngineeringWrapper and context.

        Args:
            askondataWrapper (DataEngineeringWrapper): The data engineering API wrapper for interacting with the API.
            user_id (str): The ID of the user.
            chat_id (str): The ID of the chat session.
            session (object): The session object used for data operations.

        Returns:
            BaseToolkit: An instance of CorrelationToolkit with the tools initialized.
        """
        operations: List[Dict] = [
            {
                "mode": "correlation",
                "name": "correlation",
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
        Returns the list of tools available in the Correlation toolkit.

        Returns:
            List[BaseTool]: The list of tools in the toolkit.
        """
        return self.tools
