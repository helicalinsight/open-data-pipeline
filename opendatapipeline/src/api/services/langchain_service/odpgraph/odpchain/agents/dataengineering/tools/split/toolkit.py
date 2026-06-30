from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class SplitToolkit(BaseToolkit):
    """Toolkit for performing split operations on data.

    This toolkit provides tools for splitting data using the specified operations. It is initialized
    using an API wrapper and is configured with tools that perform the split operations on data.

    :param tools: A list of tools available in the toolkit. Initialized as an empty list.
    :type tools: List[BaseTool]
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper,user_id,chat_id, session) -> BaseToolkit:
        """Creates a SplitToolkit instance from an AskOnData API wrapper.

        Initializes the toolkit with tools for split operations by defining the operations and configuring
        them with the provided API wrapper and session information.

        :param askondataWrapper: An instance of DataEngineeringWrapper used for API interactions.
        :type askondataWrapper: DataEngineeringWrapper
        :param user_id: Identifier for the user interacting with the toolkit.
        :type user_id: str
        :param chat_id: Identifier for the chat session.
        :type chat_id: str
        :param session: Session object managing interactions with the API.
        :type session: object
        :return: An instance of SplitToolkit with the configured tools.
        :rtype: BaseToolkit
        """
        operations: List[Dict] = [
            {
                "mode": "split",
                "name": "split",
                "description": get_prompt(chat_id, session),
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
                session = session
            )
            for action in operations
        ]
        return cls(tools=tools)


    def get_tools(self) -> List[BaseTool]:
        """Returns the list of tools in the SplitToolkit.

        :return: A list of tools available in the toolkit.
        :rtype: List[BaseTool]
        """
        return self.tools