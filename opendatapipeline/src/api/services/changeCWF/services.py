from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase
from ....models.mongo.mongo_factory import MongoFactory
from ....configurations.api.config import BaseConfig
from ....logger.logger import Logger, logger
from ....models.connector import MongoConnector
from src.api.services.base.service_parent import ServiceParent



class ChangeCWF(ServiceParent):
    """
    Service class for managing the current working file (CWF) in a chat system.

    :param session: The database session for interacting with MongoDB.
    :type session: object, optional
    """

    def __init__(self,session=None):
        """
        Constructor method.

        :param session: The database session for interacting with MongoDB.
        :type session: object, optional
        """
        super().__init__(session)
        self.mongo_chats = MongoFactory(self.client, "chats", session=self.session)
        self.cache: CacheBase = get_cache(session=self.session)

    @Logger.generate
    def current_working_file(self,chat_id, user_id, source_id) -> str:
            """
            Sets the current working file for a given chat based on the provided source ID.

            :param chat_id: The ID of the chat where the current working file is to be set.
            :type chat_id: str
            :param source_id: The source ID of the file to be set as the current working file.
            :type source_id: str
            :return: A dictionary with success status and message, and HTTP status code.
            :rtype: tuple(dict, int)
            :raises Exception: If there is an error in processing the request.
            """
            try:
                cache_data = self.cache.get_item(source_id, user_id, chat_id)
                self.mongo_chats.update_one(chat_id, "cwf", {"source_id":source_id, "alias": cache_data.get("dataframe_alias"), "dataframe_alias": cache_data.get("dataframe_alias")})
                return {
                    "success": True,
                    "msg": f'{cache_data["file_name"]} is the current working file.',
                }, 200
               
            except Exception as e:
                logger.error(f"An error occurred: {e}", exc_info=True)
                self._safe_abort_transaction()
                return {"success": False, "msg": f"{e}"}, 400