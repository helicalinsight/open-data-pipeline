


import uuid


from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ....exceptions.exceptions import UtilityException
from ....logger.logger import Logger, logger

from .utils import ExportUtils
from src.api.services.base.service_parent import ServiceParent

class ExportConfigService(ServiceParent):
    """Service for exporting configuration data.

    :param session: A handle to the session used for database operations.
    :type session: type
    """
    def __init__(self, session=None):
        """Constructor method

        :param session: A handle to the session used for database operations.
        :type session: type
        """
        super().__init__(session)
        self.mongo_chats = MongoFactory(self.client, "chats", session=self.session)
    
    @Logger.generate
    def export_config(self, req_data, user_id):
        """Exports configuration data and updates the chat collection.

        This method updates the export configuration for a given chat ID with the
        provided configurations. It converts dictionary string types to their original
        types before updating the MongoDB collection. If the chat ID is missing or
        an error occurs, it logs the error and returns an appropriate response.

        :param req_data: A dictionary containing request data. The expected structure is:
                        - 'chat_id': The identifier of the chat to update (string).
                        - 'configurations': A dictionary containing the configurations to be exported.
        :type req_data: dict
        :param user_id: The ID of the user initiating the export.
        :type user_id: str
        :return: A dictionary containing the success status and message. If the operation
                fails, it returns an error message.
        :rtype: dict
        :raises UtilityException: If there is an issue with exporting the configuration.
        :raises Exception: For any other unexpected errors.
        """
        try:

            chat_id = req_data.get("chat_id", None)
            configurations = req_data.get("configurations", {})

            if chat_id:
                    configurations=ExportUtils().convert_dict_strings_to_original_types(configurations)   
                    self.mongo_chats.update_one(chat_id, "configurations", configurations)
                    logger.info("Export configuration updated")
                    return {"success": True, "msg": "Export configuration updated"}, 200
            else:
                logger.error("Failed to export configuration", exc_info=True)
                raise UtilityException("Failed to export configuration")
            
        except UtilityException as e:
            logger.error(f"{e}", exc_info=True)
            self._safe_abort_transaction()  
            return {"success": False, "msg": f"{e}"}, 400

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            self._safe_abort_transaction()  
            return {"success": False, "msg": f"{e}"}, 400
