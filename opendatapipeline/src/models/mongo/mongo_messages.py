
from .mongo_factory import MongoFactory
from ...exceptions.exception import MongoException
from ...logger.logger import Logger, logger

class MongoMessages(MongoFactory): # pragma: no cover
    """
    A class for managing message-related data in a MongoDB collection. Inherits from MongoFactory.
    Provides methods for retrieving and updating messages based on chat IDs.

    Attributes:
        collection (Collection): The MongoDB collection instance used for operations.
        session (Session): The MongoDB session used for database operations.

    Methods:
        update_one_by_chat_id(chat_id, key, value):
            Updates a document in the collection based on the provided chat ID by setting the specified key to the given value.

    Exceptions:
        MongoException: If an exception occurs while fetching or updating the document.
    """
    @Logger.generate
    def update_one_by_chat_id(self, chat_id, key, value):
        """
        Updates a document in the collection based on the provided chat ID by setting the specified key to the given value.

        :param chat_id: The ID of the chat for which the document is to be updated.
        :param key: The key in the document to be updated.
        :param value: The new value to set for the specified key.
        :return: A tuple (success, modified_count) where `success` is a boolean indicating whether the operation was successful,
                 and `modified_count` is the number of documents modified (should be 1 if successful).
        :raises MongoException: If an exception occurs while updating the document.
        """
        try:
            logger.info(f"Updating data based on User id")
            result = self.collection.update_one({"chat_id": chat_id}, {"$set": {key: value}}, session=self.session)
            if result:
                return True, result.modified_count
            else:
                raise Exception(f"Got error while updating one by chat_id: chat_id : {chat_id}, key : {key} and value : {value}")
        except Exception as e: # pragma: no cover
            logger.error(f"An exception occurred: Failed to update based on chat id :{chat_id}, key :{key} and value :{value}", exc_info=True)
            raise MongoException("Failed to update based on chat id.") from e

