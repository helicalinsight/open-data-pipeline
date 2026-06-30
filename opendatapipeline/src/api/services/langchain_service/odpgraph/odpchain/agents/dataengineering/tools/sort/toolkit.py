from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class SortToolkit(BaseToolkit):
    """A toolkit for performing sorting operations on data using a set of predefined tools.

    This class extends `BaseToolkit` to provide functionality for sorting operations. It initializes tools based on 
    the `DataEngineeringWrapper` and user session information, enabling sorting tasks through a set of predefined 
    actions.

    :param tools: A list of tools available in the Sort toolkit.
    :type tools: List[BaseTool]
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper,user_id,chat_id, session) -> BaseToolkit:
        """Creates a SortToolkit instance from an AskOnData API wrapper.

        This method initializes the toolkit with tools for sorting data by wrapping operations provided by the
        `DataEngineeringWrapper`. It uses the given user and session information to configure the tools.

        :param askondataWrapper: An instance of `DataEngineeringWrapper` used for interacting with the API.
        :type askondataWrapper: DataEngineeringWrapper
        :param user_id: Identifier for the user interacting with the toolkit.
        :type user_id: str
        :param chat_id: Identifier for the chat session.
        :type chat_id: str
        :param session: Session object managing the interaction with the API.
        :type session: object
        :return: An instance of `SortToolkit` initialized with the tools for sorting operations.
        :rtype: SortToolkit
        """
        operations: List[Dict] = [
            {
                "mode": "sort",
                "name": "sort",
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
        """Returns the list of tools available in the Sort toolkit.

        :return: A list of `BaseTool` instances that can be used for sorting data.
        :rtype: List[BaseTool]
        """
        return self.tools
