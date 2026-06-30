from typing import Dict, List, Optional, Tuple, Union
from bson import ObjectId
from src.models.connector import MongoConnector
from src.exceptions.exception import *
from src.logger.logger import Logger, logger
from src.models.mongo.mongo_factory import MongoFactory
from src.models.mongo.mongo_files import MongoFiles

mongo = MongoConnector()

mongo_client = mongo.client

class File:

    def __init__(self, session):
        """
        Initializes the File service with a database session.

        Args:
            session (Session): The database session to use for MongoDB operations.
        """
        self._session = session
        self._files_collection=MongoFactory(mongo,"files",self._session)

    @Logger.generate
    def create(self, data: Dict) -> Tuple[bool, Union[ObjectId, None]]:
        """
        Inserts a new file document into the "files" collection.

        Args:
            data (dict): The data to be inserted as a new document.

        Returns:
            tuple: (bool, ObjectId) where bool indicates success and ObjectId is the ID of the inserted document.
        
        Raises:
            MongoException: If inserting the document fails.
        """
        try:
            logger.info(f"Inserting data")
            success, inserted_id = self._files_collection.insert_one(data)  
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
        Fetches a document from the "files" collection by its MongoDB ID.

        Args:
            _id (str): The MongoDB document ID to retrieve.

        Returns:
            tuple: (bool, dict) where bool indicates success and dict contains the retrieved document.
        
        Raises:
            MongoException: If fetching the document fails.
        """
        try:
            logger.info(f"Fetching data by id")
            success, result= self._files_collection.get_by_id(_id)
            if success:
                return success, result
            else:
                return False, None
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to get data by id: {_id}", exc_info=True)
            raise MongoException("Failed to get data by id") from e

    @Logger.generate
    def filter(self, query: Dict) -> Tuple[bool, Union[List[Dict], Dict]]:
        """
        Retrieves documents from the "files" collection based on the provided query filter.

        Args:
            query (dict): The MongoDB query filter.

        Returns:
            tuple: (bool, list) where bool indicates success and list contains the matching documents or array elements.

        Raises:
            MongoException: If fetching the documents fails.
        """
        try:
            logger.info("filter method started.")
            # Check if the query targets array fields or top-level fields
            is_array_query = any('.' in key for key in query.keys())
            
            if is_array_query:
                # For nested or array queries, use $filter pipeline
                conditions = [
                    {"$eq": [f"$$field.{key.split('.')[-1]}", value]} 
                    for key, value in query.items()
                ]
                field_name = query.keys()[0].split('.')[0]  # Extract the array field name

                pipeline = [
                    {"$project": {
                        "_id": 0,
                        field_name: {"$filter": {
                            "input": f"${field_name}",
                            "as": "field",
                            "cond": {"$and": conditions}
                        }}
                    }}
                ]

                result = list(self._files_collection.aggregate(pipeline))
                if result and field_name in result[0]:
                    logger.info("Fetched details successfully.")
                    return True, result[0][field_name]
                else:
                    logger.error(f"No matching documents found for query: {query}")
                    return False, []
            else:
                # For top-level queries, use a direct find
                result = list(self._files_collection.find(query))
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
    def update(self, _id: str, key: str, data: Dict, user_id: Optional[str] = None) -> Tuple[bool, int]:
        """
        Updates a file document with new data in the "files" collection.

        Args:
            _id (str): The MongoDB document ID of the file to update.
            key (str): The key to be updated.
            data (dict): The new data to set for the specified key.
            user_id (str, optional): The user ID to match for additional filtering.

        Returns:
            tuple: (bool, int) where bool indicates success and int is the count of modified documents.
        
        Raises:
            MongoException: If updating the document fails.
        """
        try:
            if user_id:
                logger.info(f"Updating data based on user id")
                success, modified_count = self._files_collection.update_one(_id, key, data, user_id)
            else:
                logger.info(f"Updating data based on id")
                success, modified_count  = self._files_collection.update_one(_id, key, data)
            if success:
                return success, modified_count
            else:
                raise Exception(f"Got error while updating: id : {_id}, key : {key}, data {data} and user_id : {user_id}")
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to update the data with id :{_id}, key :{key}, data :{data} and user_id :{user_id}", exc_info=True)
            raise MongoException("Failed to update the data.") from e

    @Logger.generate
    def delete(self, _id: str, key: Optional[str] = None, user_id: Optional[str] = None) -> Tuple[bool, int]:
        """
        Deletes a file document or a specific field in a document in the "files" collection.

        Args:
            _id (str): The MongoDB document ID of the file to delete.
            key (str, optional): The specific key to remove from the document. If not provided, the entire document is deleted.
            user_id (str, optional): The user ID to match for additional filtering.

        Returns:
            tuple: (bool, int) where bool indicates success and int is the count of deleted documents or fields.
        
        Raises:
            MongoException: If deleting the document or field fails.
        """
        try:
            success, deleted_count = self._files_collection.delete_one(_id, key, user_id)

            if success:
                return success, deleted_count
            else:
                raise Exception(f"Got error while deleting id: {_id}, key : {key} and user_id : {user_id}")
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to delete the data with id :{_id}, key :{key} and user_id :{user_id}", exc_info=True)
            raise MongoException("Failed to delete the data.") from e

    