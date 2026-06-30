from typing import Any, Dict, List, Optional, Tuple, Union
from bson import ObjectId
from src.models.connector import MongoConnector
from src.exceptions.exception import *
from src.logger.logger import Logger, logger
from src.models.mongo.mongo_factory import MongoFactory
from src.models.mongo.mongo_files import MongoFiles

mongo = MongoConnector()

mongo_client = mongo.client

class Cache:

    def __init__(self, session):
        """
        Initializes the Cache class with a database session and sets up the cache collection.

        Args:
            session (Session): The database session to use for operations.
        """
        self._session = session
        self._cache_collection=MongoFactory(mongo,"cache",self._session)

    @Logger.generate
    def create(self, data: Dict) -> Tuple[bool, Union[ObjectId, None]]:
        """
        Inserts a new document into the cache collection.

        Args:
            data (dict): The data to be inserted as a cache document.

        Returns:
            tuple: A tuple containing:
                - bool: True if the operation is successful, False otherwise.
                - ObjectId: The ID of the inserted document.

        Raises:
            MongoException: If an error occurs while inserting the document.
        """
        try:
            logger.info(f"Inserting data")
            success, inserted_id = self._cache_collection.insert_one(data)
            if success:
                return success, inserted_id
            else:
                raise Exception(f"Got error while inserting the data : {data}")
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to insert the document with data :{data}", exc_info=True)
            raise MongoException("Failed to insert the document.") from e
     

    @Logger.generate
    def get(self, _id: str) -> Tuple[bool, Optional[Dict]]:
        """
        Retrieves a document from the cache collection by its ID.

        Args:
            _id (str): The ID of the document to retrieve.

        Returns:
            tuple: A tuple containing:
                - bool: True if the document is found, False otherwise.
                - dict: The retrieved document if found, None otherwise.

        Raises:
            MongoException: If an error occurs while fetching the document.
        """
        try:
            logger.info(f"Fetching data by id")
            success, result= self._cache_collection.get_by_id(_id)
            if result:
                return True, result
            else:
                return False, None
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to get data by id: {_id}", exc_info=True)
            raise MongoException("Failed to get data by id") from e
        
    @Logger.generate
    def update_one_by_fields(self, source_id, chat_id, user_id, key, data):
        return self._cache_collection.update_one_by_fields(source_id, chat_id, user_id, key, data)
        
    @Logger.generate
    def get_by_fields(self, _id, user_id, chat_id):
        """
        Fetch a document from the collection based on the provided `_id`, `user_id`, and `chat_id`.

        Args:
            _id (str): source_id.
            user_id (str): The user ID associated with the document (required).
            chat_id (str): The chat ID associated with the document (required).

        Returns:
            tuple: (bool, dict) where bool indicates success and dict contains the document.

        Raises:
            ValueError: If any of the required fields (_id, user_id, chat_id) are not provided.
            MongoException: If fetching the document fails.
        """
        try:
            logger.info(f"Fetching data by fields")

            if not (_id and user_id and chat_id):
                raise ValueError("All fields (_id, user_id, chat_id) must be provided")
            success, result = self._cache_collection.get_by_fields(_id, user_id, chat_id)
            
            if success:
                return success, result
            else:
                return False, None
        except Exception as e:  # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to get data by fields", exc_info=True)
            raise MongoException("Failed to get data by fields") from e

        
    @Logger.generate
    def filter(self, query: Dict, array_field: Optional[str] = None) -> Tuple[bool, List]:
        """
        Retrieves documents or nested array items from the cache collection based on a query filter.

        Args:
            query (dict): The MongoDB query filter.
            array_field (str, optional): The name of the array field to filter (e.g., 'columns', 'date_format').

        Returns:
            tuple: A tuple containing:
                - bool: True if matching documents or array items are found, False otherwise.
                - list: A list of matching documents or array items.

        Raises:
            MongoException: If an error occurs while fetching the documents.
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

                result = list(self._cache_collection.aggregate(pipeline))
                if result and array_field in result[0]:
                    logger.info(f"Fetched details from array '{array_field}' successfully.")
                    return True, result[0][array_field]
                else:
                    logger.error(f"No items found in '{array_field}' matching the query: {query}")
                    return False, []

            # If no array field is specified, filter top-level fields
            result = list(self._cache_collection.find(query))
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
    def update_one_by_source_id_value(self, id, key, data):
        """
        Updates a document by setting new data based on the provided source ID.

        Args:
            id (str): The source ID to match.
            key (str): The key to be updated.
            data (dict): The new data to be set.

        Returns:
            tuple: (bool, int) where bool indicates success and int is the count of modified documents.
        
        Raises:
            MongoException: If updating the document fails.
        """
        try:
                logger.info(f"Updating data based on source id")
                success, modified_count = self._cache_collection.update_one_by_source_id_value(id, key, data)
                if success:
                    return success, modified_count
                else:
                    raise Exception(f"Got error while updating one by source_id_value: id : {id}, key : {key} and data : {data}")
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to update the data with id :{id}, key :{key} and data :{data}", exc_info=True)
            raise MongoException("Failed to update the data.") from e
        
    @Logger.generate
    def update(self, _id: str, key: str, data: Dict, user_id: Optional[str] = None) -> Tuple[bool, int]:
        """
        Updates a specific field in a cache document based on its ID and optional user ID.

        Args:
            _id (str): The ID of the document to update.
            key (str): The field to be updated.
            data (dict): The new data to set in the field.

        Returns:
            tuple: A tuple containing:
                - bool: True if the update is successful, False otherwise.
                - int: The number of modified documents.

        Raises:
            MongoException: If an error occurs while updating the document.
        """
        try:
            if user_id:
                logger.info(f"Updating data based on user id")
                success, modified_count = self._cache_collection.update_one(_id, key, data, user_id)
            else:
                logger.info(f"Updating data based on id")
                success, modified_count = self._cache_collection.update_one(_id, key, data)
            if success:
                return success, modified_count
            else:
                raise Exception(f"Got error while updating: id : {_id}, key : {key}, data {data}")
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to update the data with id :{_id}, key :{key}, data :{data}", exc_info=True)
            raise MongoException("Failed to update the data.") from e

    @Logger.generate
    def delete(self, _id: str, key: Optional[str] = None) -> Tuple[bool, int]:
        """
        Deletes a cache document or a specific field in the document based on its ID and optional user ID.

        Args:
            _id (str): The ID of the document to delete.
            key (str, optional): The field to be removed. If not provided, the entire document is deleted.

        Returns:
            tuple: A tuple containing:
                - bool: True if the deletion is successful, False otherwise.
                - int: The count of deleted documents or fields.

        Raises:
            MongoException: If an error occurs while deleting the document or field.
        """
        try:
            query = {"_id": ObjectId(_id)}
            if key:
                logger.info(f"Deleting data based on key")
                operation = {"$unset": {key: ""}}
                success, modified_count = self._cache_collection.update_one(_id, key)
                if success:
                    return success, modified_count
                else:
                    raise Exception(f"Got error while deleting: id: {id}, key : {key}")
            else:
                logger.info(f"Deleting the entire data")
                success, deleted_count = self._cache_collection.delete_one(_id)
                if success:
                    return success, deleted_count
                else:
                    raise Exception(f"Got error while deleting id: {_id}, key : {key}")
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to delete the data with id :{_id}, key :{key}", exc_info=True)
            raise MongoException("Failed to delete the data.") from e
      
    @Logger.generate
    def delete_one_by_id_value(self, id, value):
        """
        Deletes a document based on the provided key and value.

        Args:
            id (str): The key to match.
            value (str): The value to match.

        Returns:
            tuple: (bool, int) where bool indicates success and int is the count of deleted documents.
        
        Raises:
            MongoException: If deleting the document fails.
        """
        try:
            logger.info(f"Deleting the entire data")
            success, deleted_count = self._cache_collection.delete_one_by_id_value(id, value)
            if success:
                return success, deleted_count
            else:
                raise Exception(f"Got error while deleting one by id_value: id : {id} and value: {value}")
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to delete the data with id :{id} and value :{value}", exc_info=True)
            raise MongoException("Failed to delete the data.") from e
        

    @Logger.generate
    def delete_one_by_query(self, query):
        return self._cache_collection.delete_one_by_query(query)
    