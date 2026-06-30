from typing import Dict, List
from langchain_core.tools import BaseToolkit
from langchain_core.tools import BaseTool
from ...tools.wrapper import DataEngineeringWrapper
from .prompt import get_prompt
from ...common_tools.actionclass import AskOndataAction



class ExportToolkit(BaseToolkit):
    """
    Export Toolkit.

    This toolkit provides functionalities for exporting data. It sets up tools and configurations required for
    performing data export operations. The toolkit is initialized with a description for the export operation,
    and it integrates with the data engineering API to manage export tasks.

    Attributes:
        tools (List[BaseTool]): A list of tools available in the toolkit.

    Methods:
        from_aod_api_wrapper(askondataWrapper: DataEngineeringWrapper, user_id, chat_id, session) -> BaseToolkit:
            Creates an instance of the ExportToolkit using the provided DataEngineeringWrapper and context.
        
        get_tools() -> List[BaseTool]:
            Returns the list of tools in the Export toolkit.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_aod_api_wrapper(cls, askondataWrapper: DataEngineeringWrapper,user_id,chat_id, session) -> BaseToolkit:
        """
        Creates an instance of the ExportToolkit using the provided DataEngineeringWrapper and context.

        Args:
            askondataWrapper (DataEngineeringWrapper): The API wrapper used for data engineering operations.
            user_id (str): The unique identifier for the user.
            chat_id (str): The unique identifier for the chat session.
            session (object): The session object used to manage the context.

        Returns:
            BaseToolkit: An instance of ExportToolkit initialized with tools for export operations.
        """
        operations: List[Dict] = [
            {
                "mode": "export",
                "name": "export",
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
        """
        Returns the list of tools in the Export toolkit.

        Returns:
            List[BaseTool]: The tools available in the toolkit.
        """
        return self.tools
