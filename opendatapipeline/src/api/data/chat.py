from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from bson import ObjectId
from src.models.connector import MongoConnector
from src.exceptions.exception import *
from src.logger.logger import Logger, logger
from src.models.mongo.mongo_factory import MongoFactory
from src.models.mongo.mongo_files import MongoFiles

mongo = MongoConnector()

mongo_client = mongo.client

class Chat:

    def __init__(self, session):
        """Initializes the Chat class with a session and sets up the chats collection.

        Args:
            session (Session): The database session to use for MongoDB operations.
        """
        self._session = session
        self._chats_collection=MongoFactory(mongo,"chats",self._session)

    @Logger.generate
    def create(self, data: Dict[str, Any]) -> Tuple[bool, Optional[ObjectId]]:
        """
        Inserts a new chat document into the chat collection.

        Args:
            data (dict): The data to be inserted into the collection.

        Returns:
            tuple: (bool, ObjectId) where bool indicates success and ObjectId is the ID of the inserted document.

        Raises:
            MongoException: If the insertion operation fails.
        """
        try:
            logger.info(f"Inserting data")
            success, inserted_id = self._chats_collection.insert_one(data)  
            if success:
                return success, inserted_id
            else:
                raise Exception(f"Got error while inserting the data : {data}")
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to insert the document with data :{data}", exc_info=True)
            raise MongoException("Failed to insert the document.") from e
     

    @Logger.generate
    def get(self, _id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Fetches a document from the chat collection based on the provided MongoDB ID.

        Args:
            _id (str): The MongoDB document ID.

        Returns:
            tuple: (bool, dict) where bool indicates success and dict contains the retrieved document.

        Raises:
            MongoException: If the retrieval operation fails.
        """
        try:
            logger.info(f"Fetching data by id")
            success, result= self._chats_collection.get_by_id(_id)
            if result:
                return True, result
            else:
                return False, None
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to get data by id: {_id}", exc_info=True)
            raise MongoException("Failed to get data by id") from e
        
    @Logger.generate
    def filter(self, query: Dict[str, Any], array_field: Optional[str] = None) -> Tuple[bool, List[Any]]:
        """
        Fetches documents or array items from the chat collection based on the provided query filter.

        Args:
            query (dict): The MongoDB query filter.
            array_field (str, optional): The name of the array field to filter (e.g., 'files', 'history').

        Returns:
            tuple: (bool, list) where bool indicates success and list contains the matching documents or array items.

        Raises:
            MongoException: If the filtering operation fails.
        """
        try:
            logger.info("filter method started.")
            
            # Check if filtering is required on a nested array
            if array_field:
                conditions = [
                    {"$eq": [f"$$item.{key}", value]} for key, value in query.items()
                ]

                pipeline = [
                    {"$project": {
                        "_id": 0,
                        array_field: {"$filter": {
                            "input": f"${array_field}",
                            "as": "item",
                            "cond": {"$and": conditions}
                        }}
                    }}
                ]

                result = list(self._chats_collection.aggregate(pipeline))
                if result and array_field in result[0]:
                    logger.info(f"Fetched details from array '{array_field}' successfully.")
                    return True, result[0][array_field]
                else:
                    logger.error(f"No items found in '{array_field}' matching the query: {query}")
                    return False, []

            # If no array field is specified, filter top-level fields
            result = list(self._chats_collection.find(query))
            if result:
                logger.info("Fetched details successfully.")
                return True, result
            else:
                logger.error(f"No documents found matching the query: {query}")
                return False, []

        except Exception as e:  # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to fetch details with query: {query}", exc_info=True)
            raise MongoException("Failed to fetch details with the provided query.") from e

    @Logger.generate
    def update(self, _id: str, key: str, data: Any, user_id: Optional[str] = None) -> Tuple[bool, int]:
        """
        Updates a chat document with new data based on the provided MongoDB ID and optional user ID.

        Args:
            _id (str): The MongoDB document ID.
            key (str): The key to be updated.
            data (dict): The new data to be set.
            user_id (str, optional): The user ID for additional filtering.

        Returns:
            tuple: (bool, int) where bool indicates success and int is the count of modified documents.

        Raises:
            MongoException: If the update operation fails.
        """
        try:
            if user_id:
                logger.info(f"Updating data based on user id")
                success, modified_count = self._chats_collection.update_one(_id, key, data, user_id)
            else:
                logger.info(f"Updating data based on id")
                success, modified_count = self._chats_collection.update_one(_id, key, data)
            if success:
                return success, modified_count
            else:
                raise Exception(f"Got error while updating: id : {_id}, key : {key}, data {data} and user_id : {user_id}")
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to update the data with id :{_id}, key :{key}, data :{data} and user_id :{user_id}", exc_info=True)
            raise MongoException("Failed to update the data.") from e
    
    @Logger.generate
    def update_mode(self, id: str, mode):
        try:
            success, modified_count = self._chats_collection.update_one(id, "job_mode", mode)
            if success:
                return success, modified_count
            else:
                raise Exception(f"Got error while updating: id : {id}, key : mode, data {mode}")
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to update the data", exc_info=True)
            raise MongoException("Failed to update the data.") from e

    @Logger.generate
    def delete(self, _id: str, key: Optional[str] = None, user_id: Optional[str] = None) -> Tuple[bool, int]:
        """
        Deletes a chat document or a specific field from a document based on the provided MongoDB ID, key, and optional user ID.

        Args:
            _id (str): The MongoDB document ID to be deleted.
            key (str, optional): The key to be removed from the document. If not provided, the entire document is deleted.
            user_id (str, optional): The user ID for additional filtering.

        Returns:
            tuple: (bool, int) where bool indicates success and int is the count of deleted documents or fields.

        Raises:
            MongoException: If the delete operation fails.
        """
        try:

            success, deleted_count = self._chats_collection.delete_one(_id, key, user_id)

            if success:
                return success, deleted_count
            else:
                raise Exception(f"Got error while deleting id: {_id}, key : {key} and user_id : {user_id}")
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to delete the data with id :{_id}, key :{key} and user_id :{user_id}", exc_info=True)
            raise MongoException("Failed to delete the data.") from e
        
    @Logger.generate
    def append_one(self, _id: str, key: str, data: Any, user_id: Optional[str] = None) -> Tuple[bool, int]:
        """
        Appends new data to a document's array field based on the provided MongoDB ID and optional user ID.

        Args:
            _id (str): The MongoDB document ID.
            key (str): The key for the array to be updated.
            data (dict): The data to be appended.
            user_id (str, optional): The user ID for additional filtering.

        Returns:
            tuple: (bool, int) where bool indicates success and int is the count of modified documents.
        
        Raises:
            MongoException: If appending the data fails.
        """
        try:
            if user_id:
                logger.info(f"Updating data based on user id")
                success, modified_count = self._chats_collection.append_one_by_user_id(_id, key, data, user_id)
            else:
                logger.info(f"Updating data based on id")
                success, modified_count = self._chats_collection.append_one(_id, key, data)
            if success:
                return success, modified_count
            else:
                raise Exception(f"Got error while apending: id : {_id}, key : {key}, data : {data} and user_id : {user_id}")
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to append the data with id :{_id}, key :{key}, data :{data} and user_id :{user_id}", exc_info=True)
            raise MongoException("Failed to append the data.") from e
    

class JobModes(Enum):
    """available job modes"""
    LLM='llm'
    YAML='yaml'
    ACE='python'