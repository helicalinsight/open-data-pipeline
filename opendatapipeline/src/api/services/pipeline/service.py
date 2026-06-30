from .utils import PipelineHistoryUtils
from ....exceptions.exceptions import UtilityException
from ....logger.logger import Logger, logger
from src.api.services.base.service_parent import ServiceParent

class PipelineHistoryService(ServiceParent):
	"""Service class for handling pipeline history operations.

    This class provides functionality to retrieve and format pipeline history
    for a given chat ID. It interacts with utility classes to validate and
    format the chat history data.
    """
	def __init__(self, session=None):
		"""Initializes the PipelineHistoryService with a session.

        :param session: The database session to use for operations.
        :type session: Session
        """
		self.session = session
		super().__init__(session)

	@Logger.generate
	def get_pipeline_history(self, chat_id):
		"""Retrieves and formats the pipeline history for a given chat ID.

        Validates the chat ID, retrieves the history associated with it,
        and formats the history for response. If there is no history, it
        returns an empty list. If there is a 'next' history, it includes it
        in the response as well.

        :param chat_id: The ID of the chat for which to retrieve history.
        :type chat_id: str
        :return: A dictionary containing the success status and the pipeline
                 history. HTTP status code 200 for success, 400 for errors.
        :rtype: tuple(dict, int)
        :raises ValueError: If there is an issue with the chat ID or history.
        :raises UtilityException: For internal server errors related to utility operations.
        :raises Exception: For any other unexpected errors.
        """
		try:
			pipeline_history = PipelineHistoryUtils(session=self.session)
			chat = pipeline_history._validate_chat(chat_id)
			if chat is None:
				return True, 204
			# TODO: Which case is following condition handling?
			if not chat.get("history") and not chat.get("next"):
				return {"success": True, "history": [], "next": []}, 200
			
			result = pipeline_history._format_history(chat["history"], chat_id)
			result["next"] = pipeline_history._format_history(chat.get("next"), chat_id)["history"] if chat.get("next") else []
			logger.info("Successfully got the pipeline history")
			return result, 200

		except ValueError as e: # pragma: no cover
			logger.error(str(e), exc_info=True)
			return {"success": False, "msg": str(e)}, 400
		
		except UtilityException as e: # pragma: no cover
			logger.error("Internal server error", exc_info=True)
			return {"success": False, "msg": f"{e}"}, 400
		
		except Exception as e: # pragma: no cover
			logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
			return {"success": False, "msg": f"{e}"}, 400
