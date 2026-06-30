from typing import Optional
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import Field
from ..tools.wrapper import DataEngineeringWrapper

class AskOndataAction(BaseTool):
    """
    A tool that queries the Atlassian Jira API.

    Attributes:
        api_wrapper (DataEngineeringWrapper): An instance of DataEngineeringWrapper used to interact with the API.
        mode (str): The mode in which the tool operates.
        name (str): The name of the tool (optional).
        session (object): The session object used for database or API operations (optional).
        user_id (str): The ID of the user making the request (optional).
        chat_id (str): The ID of the chat session (optional).
        description (str): A brief description of the tool (optional).
    """

    api_wrapper: DataEngineeringWrapper = Field(default_factory=DataEngineeringWrapper)
    mode: str
    name: str = ""
    session: object = None
    user_id: str = None
    chat_id: str = None
    description: str = ""

    def _run(
        self,
        instructions: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """
        Executes the operation using the specified instructions and mode.

        Args:
            instructions (str): The instructions to be executed by the tool.
            run_manager (Optional[CallbackManagerForToolRun]): An optional manager for callbacks during the tool run.

        Returns:
            str: The result of the operation as a string.

        Raises:
            Exception: If an error occurs during the execution of the operation.
        """
        return self.api_wrapper.run(self.mode, instructions,self.user_id,self.chat_id, self.session)