from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class TrimToolkit(BaseToolkit):
    """Toolkit for trimming data operations.

    This toolkit provides tools for performing data trimming tasks. It initializes with tools 
    based on the operations defined and configured through the provided Data Engineering API 
    wrapper and user session information. The toolkit is designed to facilitate interaction 
    with data trimming functionalities by configuring actions with specific parameters.

    :param tools: List of tools available in the toolkit.
    :type tools: List[BaseTool]
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper,user_id,chat_id, session) -> BaseToolkit:
        """Create a TrimToolkit instance from an AskOnData API wrapper.

        This method initializes the toolkit with tools configured for trimming data operations. 
        It uses the provided Data Engineering API wrapper, user ID, chat ID, and session to create
        tools with the necessary parameters and descriptions.

        :param askondataWrapper: An instance of DataEngineeringWrapper to interact with data operations.
        :type askondataWrapper: DataEngineeringWrapper
        :param user_id: Identifier for the user interacting with the toolkit.
        :type user_id: str
        :param chat_id: Identifier for the chat session.
        :type chat_id: str
        :param session: Session object managing the interaction with the tools.
        :type session: object
        :return: An instance of TrimToolkit configured with the specified tools.
        :rtype: BaseToolkit
        """
        operations: List[Dict] = [
            {
                "mode": "trim",
                "name": "trim",
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
                session= session
            )
            for action in operations
        ]
        return cls(tools=tools)


    def get_tools(self) -> List[BaseTool]:
        """Retrieve the list of tools in the TrimToolkit.

        This method returns the tools configured within the toolkit.

        :return: List of tools available in the toolkit.
        :rtype: List[BaseTool]
        """
        return self.tools