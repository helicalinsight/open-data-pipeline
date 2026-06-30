from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class UpperCaseToolkit(BaseToolkit):
    """Toolkit for performing uppercase transformations on data.

    The `UpperCaseToolkit` class provides a set of tools for transforming data to uppercase. It uses
    the `AskOndataAction` class to interact with a data engineering API and integrate with the specified
    user and chat session. 

    Tools are initialized based on the specified configuration and prompt details.

    :param tools: A list of tools available in the toolkit.
    :type tools: List[BaseTool]
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper,user_id,chat_id, session) -> BaseToolkit:
        """Create an instance of the toolkit from the given API wrapper.

        This method initializes the toolkit with a set of operations for performing uppercase
        transformations. It configures the tools based on the provided user ID, chat ID, and session.

        :param askondataWrapper: The data engineering API wrapper used for interacting with data operations.
        :type askondataWrapper: DataEngineeringWrapper
        :param user_id: Identifier for the user interacting with the toolkit.
        :type user_id: str
        :param chat_id: Identifier for the chat session.
        :type chat_id: str
        :param session: Session object managing the interaction with the tools.
        :type session: object
        :return: An instance of `UpperCaseToolkit` initialized with the available tools.
        :rtype: BaseToolkit
        """
        operations: List[Dict] = [
            {
                "mode": "uppercase",
                "name": "uppercase",
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
        """Retrieve the list of tools in the UpperCase toolkit.

        :return: A list of tools available for performing uppercase transformations.
        :rtype: List[BaseTool]
        """
        return self.tools
