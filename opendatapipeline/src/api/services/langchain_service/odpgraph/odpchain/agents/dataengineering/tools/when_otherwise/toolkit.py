from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class WhenOtherwiseToolkit(BaseToolkit):
    """WhenOtherwise Toolkit.

    The `WhenOtherwiseToolkit` class provides a toolkit for handling conditional operations
    based on 'when' and 'otherwise' logic. It allows for the execution of specific actions
    depending on the conditions defined within the toolkit.

    This toolkit is initialized with a list of operations that define the conditions and actions
    to be performed. The operations are used to configure tools that interact with a data engineering
    API wrapper.

    :param tools: List of tools available in the toolkit. This is initialized as an empty list.
    :type tools: List[BaseTool]
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper,user_id,chat_id, session) -> BaseToolkit:
        """Create a `WhenOtherwiseToolkit` instance from a data engineering API wrapper.

        This method configures the toolkit with operations based on the provided user and chat context.
        It sets up tools that use the specified API wrapper to perform actions based on 'when' and 'otherwise'
        conditions.

        :param askondataWrapper: The data engineering API wrapper used for performing operations.
        :type askondataWrapper: DataEngineeringWrapper
        :param user_id: Identifier for the user interacting with the toolkit.
        :type user_id: str
        :param chat_id: Identifier for the chat session.
        :type chat_id: str
        :param session: Session object managing the interaction with the toolkit.
        :type session: object
        :return: An instance of `WhenOtherwiseToolkit` configured with the specified tools.
        :rtype: BaseToolkit
        """
        operations: List[Dict] = [
            {
                "mode": "when_otherwise",
                "name": "when_otherwise",
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
        """Retrieve the tools available in the WhenOtherwise toolkit.

        :return: List of tools configured in the toolkit.
        :rtype: List[BaseTool]
        """
        return self.tools
