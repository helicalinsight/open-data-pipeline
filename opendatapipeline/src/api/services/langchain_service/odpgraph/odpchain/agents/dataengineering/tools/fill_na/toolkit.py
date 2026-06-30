from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class FillNaToolkit(BaseToolkit):
    """
    FillNaToolkit provides tools for filling missing values in datasets.

    This toolkit utilizes the `AskOndataAction` to create a tool for filling missing values based on user specifications.
    It is used in conjunction with an `DataEngineeringWrapper` and a language model to perform operations related to missing data.

    Attributes:
        tools (List[BaseTool]): A list of tools available in the toolkit.

    Methods:
        from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
            Creates an instance of `FillNaToolkit` from the given `DataEngineeringWrapper` and configurations.

        get_tools(self) -> List[BaseTool]:
            Returns the list of tools in the `FillNaToolkit`.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
        """
        Creates a `FillNaToolkit` instance from the provided `DataEngineeringWrapper` and configuration parameters.

        Args:
            askondataWrapper (DataEngineeringWrapper): The API wrapper for data engineering tasks.
            user_id (str): The unique identifier for the user.
            chat_id (str): The unique identifier for the chat session.
            session (object): The session object used to manage the context.

        Returns:
            BaseToolkit: An instance of `FillNaToolkit` with configured tools.
        """
        operations: List[Dict] = [
            {
                "mode": "fill_na",
                "name": "fill_na",
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
        """
        Returns the list of tools available in the `FillNaToolkit`.

        Returns:
            List[BaseTool]: A list of tools for filling missing values.
        """
        return self.tools
