from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import UNION_TOOL_PROMPT
from ...common_tools.actionclass import AskOndataAction



class UnionToolkit(BaseToolkit):
    """Toolkit for performing union operations on data.

    The `UnionToolkit` class provides tools for executing union operations using the Data Engineering API.
    It initializes tools based on the provided API wrapper and user session, specifically for union-related tasks.

    :param tools: List of tools available in the toolkit.
    :type tools: List[BaseTool]
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper,user_id,chat_id,session) -> BaseToolkit:
        """Create a toolkit instance from the Data Engineering API wrapper.

        Initializes the toolkit with a union operation tool using the provided API wrapper, user ID, chat ID,
        and session. The tool is configured for executing union operations on data.

        :param askondataWrapper: API wrapper for data engineering operations.
        :type askondataWrapper: DataEngineeringWrapper
        :param user_id: Identifier for the user interacting with the toolkit.
        :type user_id: str
        :param chat_id: Identifier for the chat session.
        :type chat_id: str
        :param session: Session object managing the interaction with the tools.
        :type session: object
        :return: An instance of the `UnionToolkit` class with the initialized tools.
        :rtype: BaseToolkit
        """
        operations: List[Dict] = [
            {
                "mode": "union",
                "name": "union",
                "description": UNION_TOOL_PROMPT,
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
        """Retrieve the tools in the Union toolkit.

        :return: List of tools available in the toolkit.
        :rtype: List[BaseTool]
        """
        return self.tools
