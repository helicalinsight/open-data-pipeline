from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class RenameColumnsToolkit(BaseToolkit):
    """A toolkit for renaming columns in data using a set of predefined tools.

    This class provides methods to initialize tools specifically for renaming columns based on an API wrapper
    and user session information. It extends from `BaseToolkit` and includes functionality to create and retrieve
    tools for column renaming tasks.

    :param tools: A list of tools available in the RenameColumns toolkit.
    :type tools: List[BaseTool]
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper,user_id,chat_id, session) -> BaseToolkit:
        """Creates a RenameColumnsToolkit instance from an AskOnData API wrapper.

        This method initializes the toolkit with a set of tools for renaming columns by wrapping operations
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
        :return: An instance of `RenameColumnsToolkit` initialized with the tools for renaming columns.
        :rtype: RenameColumnsToolkit
        """
        operations: List[Dict] = [
            {
                "mode": "rename_columns",
                "name": "rename_columns",
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
        """Returns the list of tools available in the RenameColumns toolkit.

        :return: A list of `BaseTool` instances that can be used for renaming columns.
        :rtype: List[BaseTool]
        """
        return self.tools