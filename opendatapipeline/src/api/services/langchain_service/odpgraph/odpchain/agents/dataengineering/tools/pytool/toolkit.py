from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_pytool_prompt
from ...common_tools.actionclass import AskOndataAction


class PyToolToolkit(BaseToolkit):
    """A toolkit for performing Pandas operations.

    This toolkit provides tools for executing Pandas operations. It initializes with a set of tools
    configured for Pandas tasks using the `AskOndataAction` class. The toolkit is constructed based on
    a Data Engineering API wrapper and specific user and session information.

    :param tools: A list of tools available in the toolkit.
    :type tools: List[BaseTool]
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper,user_id,chat_id, session, cwf_name) -> BaseToolkit:
        """Creates a toolkit instance from the Data Engineering API wrapper.

        This class method initializes the toolkit with tools for performing Pandas operations. It uses
        the provided `DataEngineeringWrapper` to create an action for Pandas operations and configures it
        with the given user and session information.

        :param askondataWrapper: The Data Engineering API wrapper used to interact with the backend services.
        :type askondataWrapper: DataEngineeringWrapper
        :param user_id: Identifier for the user interacting with the toolkit.
        :type user_id: str
        :param chat_id: Identifier for the chat session.
        :type chat_id: str
        :param session: Session object managing the interaction with the tools.
        :type session: object
        :return: An instance of `PyToolToolkit` initialized with Pandas operation tools.
        :rtype: BaseToolkit
        """
        operations: List[Dict] = [
            {
                "mode": "pytool",
                "name": "pytool",
                "description": get_pytool_prompt(chat_id, session, cwf_name),
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
        """Retrieves the list of tools in the SQLOperations toolkit.

        :return: A list of tools available in the toolkit.
        :rtype: List[BaseTool]
        """
        return self.tools
