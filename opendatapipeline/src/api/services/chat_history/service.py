from ...data.cache import Cache
from ....etl.metadata.meta_processor import MetaProcessor
from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory

from ....configurations.api.config import BaseConfig
from ....exceptions.exceptions import UtilityException
from ....logger.logger import Logger, logger
from src.api.services.base.service_parent import ServiceParent


from .utils import ChatHistoryUtil

class ChatHistoryService(ServiceParent):
    """
    Service class for managing chat history operations in a chat system.

    :param session: The database session for interacting with MongoDB.
    :type session: object, optional
    """
    def __init__(self, session=None):
        """
        Constructor method.

        :param session: The database session for interacting with MongoDB.
        :type session: object, optional
        """
        super().__init__(session)
        self.mongo_langchain = MongoFactory(self.client, "langchain", session=self.session)
        self.mongo_chats = MongoFactory(self.client, "chats", session=self.session)
        self.mongo_cache = MongoFactory(self.client, "cache", session=self.session)
    
    @Logger.generate
    def get_chat_history(self, user_id, chat_id, offset, limit):
        """
        Retrieves chat history for a specific chat.

        :param user_id: The ID of the user requesting the chat history.
        :type user_id: str
        :param chat_id: The ID of the chat whose history is to be retrieved.
        :type chat_id: str
        :param offset: The starting index for pagination.
        :type offset: int
        :param limit: The maximum number of chat history entries to retrieve.
        :type limit: int
        :return: A dictionary containing chat history, pagination status, and HTTP status code.
        :rtype: tuple(dict, int)
        :raises Exception: If there is an error in retrieving the chat history.
        """

        try:
            if chat_id is None:
                logger.warning(f"Received None chat_id which is invalid")
                return {
                    'chat_history': [],
                    'has_more': False
                }, 200
            
            _, messages = self.mongo_langchain.get_by_id_and_value("chat_id", chat_id)
            if not messages:
                logger.info("No messages found in langchain collection")
                # raise Exception(f"No message history found with user_id: {user_id}, chat_id: {chat_id}, offset: {offset} and limit: {limit}") # pragma: no cover

            events = messages.get('messages', []) if messages else []

            chat_history = [
                {
                    'isUser': event.get('event') == 'user',
                    'text': event.get("message", ""),
                    'timestamp': event.get('timestamp', ''),
                    'message_id': event.get('message_id', ''),
                }
                for event in events
            ]
            chat_history = chat_history[::-1]
            chat_count = len(chat_history)
            limit = min(limit, chat_count)

            paginated_chats = chat_history[offset:offset + limit]
            has_more = offset + limit < chat_count
            logger.info("Successfully performed get chat history")
            return {
                'chat_history': paginated_chats,
                'has_more': has_more,
            }

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {
                'chat_history': [],
                'has_more': False,
                "messaage": f"{e}"
            }, 200

    @Logger.generate
    def delete_chat_history(self, user_id, chat_id):
        """
        Deletes the chat history for a specific chat.

        :param user_id: The ID of the user requesting the deletion.
        :type user_id: str
        :param chat_id: The ID of the chat whose history is to be deleted.
        :type chat_id: str
        :return: A dictionary containing status and message about the deletion operation.
        :rtype: dict
        :raises UtilityException: If there is an error in utility operations.
        :raises Exception: If there is an error in deleting the chat history.
        """
        chat_util = ChatHistoryUtil(session=self.session)
        
        try:
            status , chat = self.mongo_chats.get_by_id(chat_id)
            if not chat:
                raise Exception(f"Chat ID not found for the user_id: {user_id} and chat_id: {chat_id}") # pragma: no cover
            
            try:
                status, langchain = self.mongo_langchain.get_by_id_and_value("chat_id", chat_id)
            except:
                langchain=None
            
            meta_processor = MetaProcessor(self.session)
            status, cache_docs = self.mongo_cache.get_all_by_user_id_key_value(user_id, "chat_id", chat_id)
            if status:
                for doc in cache_docs:
                    meta_processor.delete_files(chat_id, doc["source_id"], should_save_history=False)
            
            self.mongo_chats.update_one(chat_id, "job_mode", "llm")
            if langchain:
                status_clear_chat_data = chat_util._clear_chat_data(langchain)
                status_clear_chat_history = chat_util._clear_chat_history(chat)
                if status_clear_chat_data and status_clear_chat_history:
                    logger.info("Successfully deleted the chat history")
                    return {
                        'status': True,
                        'chat_history': [],
                        'has_more': False,
                        'selected_files': [],
                        'loaded_files': [],
                        'columns': [],
                        'metadata': {},
                        "message": "Chat history deleted successfully"
                    }
                else:
                    raise Exception(f"No history found for the user_id: {user_id} and chat_id: {chat_id}") # pragma: no cover
            else:
                status_clear_chat_history = chat_util._clear_chat_history(chat)
                logger.info("No history found..")
                return {
                        'status': True,
                        'chat_history': [],
                        'has_more': False,
                        'selected_files': [],
                        'loaded_files': [],
                        'columns': [],
                        'metadata': {},
                        "message": "Chat history deleted successfully"
                    }
            
        except UtilityException as e: # pragma: no cover
            logger.error(f"{e}", exc_info=True)
            self.session.abort_transaction()
            return {"status": False, "message": f"{e}"}, 500

        except Exception as e: # pragma: no cover
            logger.error(f"Error deleting chat history: {e}", exc_info=True)
            self.session.abort_transaction()
            return {"status": False, "message": f"{e}"}, 500
            # return {"status": False, "message": "Failed to delete chat history"}, 500