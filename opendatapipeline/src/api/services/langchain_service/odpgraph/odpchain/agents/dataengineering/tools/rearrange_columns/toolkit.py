from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class RearrangeColumnsToolkit(BaseToolkit):
    """A toolkit for rearranging columns in data using a set of predefined tools.

    This class provides methods to initialize tools specifically for rearranging columns based on an API wrapper
    and user session information. It extends from `BaseToolkit` and includes functionality to create and retrieve
    tools for column rearrangement tasks.

    :param tools: A list of tools available in the RearrangeColumns toolkit.
    :type tools: List[BaseTool]
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper,user_id,chat_id, session) -> BaseToolkit:
        """Creates a RearrangeColumnsToolkit instance from an AskOnData API wrapper.

        This method initializes the toolkit with a set of tools for rearranging columns by wrapping operations
        provided by the `DataEngineeringWrapper`. It uses the provided user and session information to configure
        the tools.

        :param askondataWrapper: An instance of `DataEngineeringWrapper` used for interacting with the API.
        :type askondataWrapper: DataEngineeringWrapper
        :param user_id: Identifier for the user interacting with the toolkit.
        :type user_id: str
        :param chat_id: Identifier for the chat session.
        :type chat_id: str
        :param session: Session object managing the interaction with the API.
        :type session: object
        :return: An instance of `RearrangeColumnsToolkit` initialized with the tools for column rearrangement.
        :rtype: RearrangeColumnsToolkit
        """
        operations: List[Dict] = [
            {
                "mode": "rearrange_columns",
                "name": "rearrange_columns",
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
        """Returns the list of tools available in the RearrangeColumns toolkit.

        :return: A list of `BaseTool` instances that can be used for column rearrangement tasks.
        :rtype: List[BaseTool]
        """
        return self.tools
