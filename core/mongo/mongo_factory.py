
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from bson import ObjectId
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.client_session import ClientSession
from pymongo.cursor import Cursor
from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError

from core.exceptions import MongoException
from core.logger import Logger

class MongoFactory:
    """
    Factory class for interacting with MongoDB collections.
    Unified implementation for core library.
    """
    def __init__(self, mongo: Union[MongoClient, Database, Any], collection_name: str, session: Optional[ClientSession] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize the MongoFactory.

        Args:
            mongo (MongoClient or Database): The MongoDB client or Database instance.
            collection_name (str): The name of the collection to interact with.
            session (ClientSession, optional): The MongoDB session instance for transactions.
            logger (logging.Logger, optional): Custom logger instance to use.
        """
        self.session = session
        self.logger = logger
        
        try:
            # Flexible initialization: mongo can be a client (with collection access) or a database object
            # If it's a client, we assume it has attribute access or item access for collection
            # However, looking at usage: self.collection = self.collection_name[collection_name] 
            # implies 'mongo' argument was actually a 'database' object (renamed to collection_name in original code which was confusing)
            # Let's support passing the database object directly.
            
            # In opendatapipeline: self.collection_name was assigned a DATABASE object (client.user_sessions etc)
            # In spark: self.mongo were passed, and self.collection = getattr(self.mongo, collection_name)
            
            # Unified approach: Expect 'mongo' to be the DATABASE object (or equivalent that supports [name] or getattr)
            
            if hasattr(mongo, collection_name):
                 self.collection = getattr(mongo, collection_name)
            elif hasattr(mongo, '__getitem__'):
                 self.collection = mongo[collection_name]
            else:
                 # Fallback if specific getitem/getattr fails but it might be valid object
                 self.collection = mongo[collection_name]
            
            Logger.info(f"MongoFactory initialized successfully for collection '{collection_name}'", logger_instance=self.logger)
            
        except Exception as e:
            Logger.error(f"MongoFactory initialization failed: {e}", exc_info=True, logger_instance=self.logger)
            self.collection = None
            raise MongoException(f"Failed to initialize MongoFactory: {e}")

    def find(self, query: Dict[str, Any]) -> Cursor:
        """
        Retrieve documents from the MongoDB collection that match the specified query.
        """
        return self.collection.find(query, session=self.session)

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform an aggregation query on the collection based on the provided pipeline.

        Args:
            pipeline (list): The MongoDB aggregation pipeline.

        Returns:
            list: A list of documents returned by the aggregation.
            
        Raises:
            MongoException: If the aggregation query fails.
        """
        try:
            Logger.info(f"Performing aggregation with pipeline: {pipeline}", logger_instance=self.logger)
            result = list(self.collection.aggregate(pipeline, session=self.session))
            for doc in result:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            return result
        except Exception as e:
            Logger.error(f"The Mongo exception occurred: Failed to perform aggregation: {pipeline}, Exception: {e}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to perform aggregation.") from e

    @Logger.generate
    def get_by_id(self, _id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Fetch a document from the collection based on the provided MongoDB ID.
        Returns (bool, dict).
        """
        try:
            Logger.info(f"Fetching data by id", logger_instance=self.logger)
            result= self.collection.find_one(ObjectId(_id), session=self.session)
            if result:
                return True, result
            else:
                return False, None
        except Exception as e:
            Logger.error(f"The Mongo exception occurred: Failed to get data by id: {_id}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to get data by id") from e
    
    @Logger.generate
    def get_by_user_id_job_id(self, job_id: str, user_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Finds the data from mongo based on the user id and job id.
        From Spark/DLT implementation.
        Returns: (bool, dict) - Unified return type
        """
        try:
            Logger.debug(f"Fetching data by user_id and job_id", logger_instance=self.logger)
            query = {
                "_id": ObjectId(job_id),
                "user_id": user_id,
            }
            result = self.collection.find_one(query, session=self.session)
            if result:
                return True, result
            else:
                return False, None
        except Exception as e:
            Logger.error(f"An exception occurred: {str(e)}", logger_instance=self.logger)
            raise MongoException(f"Failed to fetch details by user_id and job_id") from e

    @Logger.generate
    def get_by_fields(self, source_id: str, user_id: str, chat_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Fetch a document from the collection based on the provided `source_id`, `user_id`, and `chat_id`.
        """
        try:
            Logger.info(f"Fetching data by fields", logger_instance=self.logger)

            if not (source_id and user_id and chat_id):
                raise ValueError("All fields (source_id, user_id, chat_id) must be provided")

            # Build the query with all three fields
            query = {
                "source_id": source_id,
                "user_id": user_id,
                "chat_id": chat_id
            }

            result = self.collection.find_one(query, session=self.session)

            if result:
                return True, result
            else:
                return False, None
        except Exception as e:
            Logger.error(f"The Mongo exception occurred: Failed to get data by fields", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to get data by fields") from e
    
    @Logger.generate
    def filter_one(self, query: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Fetch a document from the collection based on the provided query.
        """
        try:
            Logger.info(f"Fetching data by fields", logger_instance=self.logger)

            result = self.collection.find_one(query, session=self.session)

            if result:
                return True, result
            else:
                return False, None
        except Exception as e:
            Logger.error(f"The Mongo exception occurred: Failed to get data by query: {query}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to get data by fields") from e

        
    @Logger.generate
    def get_by_file_id_and_file_name(self, file_id: str, file_name: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Fetch a document from the collection based on the provided file ID and file name.
        """
        try:
            Logger.info(f"Fetching data by file_id and file_name", logger_instance=self.logger)
            result = self.collection.find_one({"files": {"$elemMatch": {"file_id": file_id, "file_name": file_name}}}, session=self.session)
            if result:
                return True, result
            else:
                raise Exception(f"No data found for file_id : {file_id} and file_name : {file_name}")
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to get the data by file id :{file_id} and file name :{file_name}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to get the data by file id and file name.") from e

    @Logger.generate
    def get_by_user_id(self, user_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Fetch a document from the collection based on the provided user ID.
        """
        try:
            Logger.info(f"Fetching data by user_id", logger_instance=self.logger)
            result=self.collection.find_one({"user_id": user_id}, session=self.session)
            if result:
                return True, result
            else:
                # Standardizing: opendatapipeline raised Exception here, keeping it for now but beware of control flow
                # For unification, if spark expects None, this raise might be breaking.
                # However, task says 'Implement based on opendatapipeline version'.
                raise Exception(f"No data found for user_id : {user_id}")
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to get the data by user id :{user_id}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to get the data by user id.") from e

    @Logger.generate
    def get_all_by_user_id(self, user_id: str) -> Tuple[bool, Optional[Cursor]]:
        """
        Fetch all documents from the collection based on the provided user ID.
        """
        try:
            Logger.info(f"Fetching data by user_id", logger_instance=self.logger)
            result=self.collection.find({"user_id": user_id}, session=self.session)
            if result:
                return True, result
            else:
                raise Exception(f"No data found for user_id : {user_id}")
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to get the data by user id :{user_id}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to get the data by user id.") from e
        
    @Logger.generate
    def get_by_user_id_key_value(self, user_id: str, key: str, value: Any) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Fetch a document from the collection based on the provided user ID and key-value pair.
        """
        try:
            Logger.info(f"Fetching data by user_id", logger_instance=self.logger)
            query = {
                "user_id": user_id,
                key: value,
            }
            result=self.collection.find_one(query, session=self.session)
            if result:
                return True, result
            else:
                raise Exception(f"No data found for user_id : {user_id}, key : {key} and value : {value}")
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to get the data by user id :{user_id} and key :{key}, value :{value}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to get the data by user id and key value.") from e
        
    @Logger.generate
    def get_by_id_and_value(self, id: str, value: Any) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Fetch a document from the collection based on the provided key-value pair.
        """
        try:
            Logger.info(f"Fetching data by key - {id}", logger_instance=self.logger)
            query = {
                id: value,
            }
            result= self.collection.find_one(query, session=self.session)
            if result:
                return True, result
            else:
                Logger.warning(f"No data found for key: {id} value: {value}", logger_instance=self.logger)
                return False, None
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to get the data by id :{id} and value :{value}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to get the data.") from e
        
    @Logger.generate
    def get_all_by_user_id_key_value(self, user_id: str, key: str, value: Any) -> Tuple[bool, Union[List[Any], Cursor]]:
        """
        Fetches all documents from the collection based on the provided user ID and key-value pair.
        """
        try:
            Logger.info(f"Fetching data by user_id", logger_instance=self.logger)
            query = {
                "user_id": user_id,
                key: value,
            }
            result=self.collection.find(query, session=self.session)
            if result:
                return True, result
            else:
                return False, []
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to get the data by user id :{user_id}, key: {key} and value :{value}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to get the data.") from e

    @Logger.generate
    def get_all_by_id_key_value(self, key: str, value: Any) -> Tuple[bool, Optional[Cursor]]:
        """
        Fetches all documents from the collection based on the provided key-value pair.
        """
        try:
            Logger.info(f"Fetching data by key value", logger_instance=self.logger)
            query = {
                key: value,
            }
            result=self.collection.find(query, session=self.session)
            if result:
                return True, result
            # Should we raise/return False if not found? Original code returns True/result if found, handles generic exception.
            # Implicitly returns None if not found and no exception (though find returns cursor so always valid?)
            # Cursor is always truthy. 'if result:' is always true for cursor.
            # But adhering to structure.
            return True, result
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to get the data by key: {key} and value :{value}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to get the data.") from e
        
    @Logger.generate
    def insert_one(self, data: Dict[str, Any]) -> Tuple[bool, Optional[ObjectId]]:
        """
        Inserts a new document into the collection with a specified key and data.
        """
        try:
            Logger.info(f"Inserting data", logger_instance=self.logger)
            result = self.collection.insert_one(data, session=self.session)  
            if result:
                return True, result.inserted_id
            else:
                raise Exception(f"Got error while inserting the data : {data}")
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to insert the document with data :{data}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to insert the document.") from e
        
    @Logger.generate
    def insert_document(self, data: Dict[str, Any]) -> Tuple[bool, Optional[ObjectId]]:
        """
        Inserts a new document into the collection.
        """
        try:
            Logger.info(f"Inserting data", logger_instance=self.logger)
            result = self.collection.insert_one(data, session=self.session)
            if result:
                return True, result.inserted_id
            else:
                raise Exception(f"Got error while inserting the data : {data}")
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to insert the document with data :{data}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to insert the document.") from e

    @Logger.generate
    def update_one(self, _id: str, key: str, data: Any, user_id: Optional[str] = None) -> Tuple[bool, int]:
        """
        Updates a document by setting new data based on the provided MongoDB ID and optional user ID.
        """
        try:
            if user_id:
                Logger.info(f"Updating data based on user id", logger_instance=self.logger)
                result = self.collection.update_one({"_id": ObjectId(_id), "user_id": user_id}, {"$set": {key: data}}, session=self.session)
            else:
                Logger.info(f"Updating data based on id", logger_instance=self.logger)
                result = self.collection.update_one({"_id": ObjectId(_id)}, {"$set": {key: data}}, session=self.session)
            if result:
                return True, result.modified_count
            else:
                Logger.info(f"No data updated", logger_instance=self.logger)
                return False, 0
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to update the data with id :{_id}, key :{key}, data :{data} and user_id :{user_id}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to update the data.") from e

    @Logger.generate
    def append_one(self, _id: str, key: str, data: Any, user_id: Optional[str] = None) -> Tuple[bool, int]:
        """
        Appends new data to a document's array field based on the provided MongoDB ID and optional user ID.
        """
        try:
            if user_id:
                Logger.info(f"Updating data based on user id", logger_instance=self.logger)
                result = self.collection.update_one({"_id": ObjectId(_id), "user_id": user_id}, {"$set": {key: data}}, session=self.session)
            else:
                Logger.info(f"Updating data based on id", logger_instance=self.logger)
                result = self.collection.update_one({"_id": ObjectId(_id)}, {"$push": {key: data}}, session=self.session)
            if result:
                return True, result.modified_count
            else:
                raise Exception(f"Got error while apending: id : {_id}, key : {key}, data : {data} and user_id : {user_id}")
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to append the data with id :{_id}, key :{key}, data :{data} and user_id :{user_id}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to append the data.") from e
        
    @Logger.generate
    def update_one_by_user_id(self, user_id: str, key: str, data: Any) -> Tuple[bool, int]:
        """
        Updates a document by setting new data based on the provided user ID.
        """
        try:
                Logger.info(f"Updating data based on User id", logger_instance=self.logger)
                result = self.collection.update_one({"user_id": user_id}, {"$set": {key: data}}, session=self.session)
                if result:
                    return True, result.modified_count
                else:
                    raise Exception(f"Got error while updating one by user_id: {user_id}, key : {key} and data : {data}")
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to update the data with user_id :{user_id}, key :{key} and data :{data}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to update the data.") from e

    @Logger.generate
    def update_one_by_fields(self, source_id: str, chat_id: str, user_id: str, key: str, data: Any) -> Tuple[bool, int]:
        try:
            Logger.info(f"Update document based on source_id, chat_id, user_id", logger_instance=self.logger)
            result = self.collection.update_one(
                {
                    "source_id": source_id,
                    "chat_id": chat_id,
                    "user_id": user_id
                },
                {
                    "$set": {key: data}
                },
                session=self.session
            )
            if result:
                return True, result.modified_count
            else:
                return False, 0
        except Exception as e:
            Logger.error(f"Failed to update document for source_id {source_id}, user_id {user_id}, chat_id {chat_id}", logger_instance=self.logger)
            raise MongoException("Failed to update the data.") from e
    
    @Logger.generate
    def update_one_by_source_id_value(self, id: str, key: str, data: Any) -> Tuple[bool, int]:
        """
        Updates a document by setting new data based on the provided source ID.
        """
        try:
                Logger.info(f"Updating data based on source id", logger_instance=self.logger)
                result = self.collection.update_one({"source_id": id}, {"$set": {key: data}}, session=self.session)
                if result:
                    return True, result.modified_count
                else:
                    raise Exception(f"Got error while updating one by source_id_value: id : {id}, key : {key} and data : {data}")
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to update the data with id :{id}, key :{key} and data :{data}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to update the data.") from e
    
    @Logger.generate
    def update_by_chat_id_value(self, id: str, key: str, data: Any) -> Tuple[bool, int]:
        """
        Updates a document by setting new data based on the provided chat ID.
        """
        try:
                Logger.info(f"Updating data based on source id", logger_instance=self.logger)
                result = self.collection.update_one({"chat_id": id}, {"$set": {key: data}}, session=self.session)
                if result:
                    return True, result.modified_count
                else:
                    raise Exception(f"Got error while updating by chat_id_value: id : {id}, key : {key} and data : {data}")
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to update the data with id :{id}, key :{key} and data :{data}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to update the data.") from e

    @Logger.generate
    def append_one_by_user_id(self, user_id: str, key: str, data: Any) -> Tuple[bool, int]:
            """
            Appends new data to an array field in the document based on the provided user ID.
            """
            try:
                Logger.info(f"Updating data based on User id", logger_instance=self.logger)
                result = self.collection.update_one({"user_id": user_id}, {"$push": {key: data}}, session=self.session)
                if result:
                    return True, result.modified_count
                else:
                    raise Exception(f"Got error while appending one by user_id: {user_id}, key : {key} and data : {data}")
            except OperationFailure as e:
                raise OperationFailure(e)    
            except Exception as e: 
                Logger.error(f"The Mongo exception occurred: Failed to update the data with user_id :{user_id}, key :{key} and data :{data}", exc_info=True, logger_instance=self.logger)
                raise MongoException("Failed to update the data.") from e
            
    @Logger.generate
    def update_all(self, _id: str, data: Dict[str, Any], user_id: Optional[str] = None) -> Tuple[bool, int]:
        """
        Updates or adds multiple data fields to an existing document based on the provided MongoDB ID and optional user ID.
        """
        try:
            if user_id:
                Logger.info(f"Updating data based on user id", logger_instance=self.logger)
                result = self.collection.update_one({"_id": ObjectId(_id), "user_id": user_id}, {"$set": data}, session=self.session)
            else:
                Logger.info(f"Updating data based on id", logger_instance=self.logger)
                result = self.collection.update_one({"_id": ObjectId(_id)}, {"$set": data}, session=self.session)
            if result:
                return True, result.modified_count
            else:
                raise Exception(f"Got error while updating all: id: {_id}, data : {data} and user_id : {user_id}")
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to update the data with id :{_id}, data :{data} and user_id :{user_id}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to update the data.") from e

    @Logger.generate
    def delete_one(self, _id: str, key: Optional[str] = None, user_id: Optional[str] = None) -> Tuple[bool, int]:
        """
        Deletes a document or a specific field from a document based on the provided MongoDB ID and optional key and user ID.
        """
        try:
            query = {"_id": ObjectId(_id)}
            if user_id:
                Logger.info(f"Deleting data based on user id", logger_instance=self.logger)
                query["user_id"] = user_id

            if key:
                Logger.info(f"Deleting data based on key", logger_instance=self.logger)
                operation = {"$unset": {key: ""}}
                result = self.collection.update_one(query, operation, session=self.session)
                if result:
                    return True, result.modified_count
                else:
                    raise Exception(f"Got error while deleting: id: {_id}, key : {key} and user_id : {user_id}")
            else:
                Logger.info(f"Deleting the entire data", logger_instance=self.logger)
                result = self.collection.delete_one(query, session=self.session)
                if result:
                    return True, result.deleted_count
                else:
                    raise Exception(f"Got error while deleting id: {_id}, key : {key} and user_id : {user_id}")
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to delete the data with id :{_id}, key :{key} and user_id :{user_id}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to delete the data.") from e


    @Logger.generate
    def delete_one_by_id_value(self, id: str, value: Any) -> Tuple[bool, int]:
        """
        Deletes a document based on the provided key and value.
        """
        try:
            query = {id: value}
            Logger.info(f"Deleting the entire data", logger_instance=self.logger)
            result = self.collection.delete_one(query, session=self.session)
            if result:
                return True, result.deleted_count
            else:
                raise Exception(f"Got error while deleting one by id_value: id : {id} and value: {value}")
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to delete the data with id :{id} and value :{value}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to delete the data.") from e
        
    @Logger.generate
    def delete_one_by_query(self, query: Dict[str, Any]) -> Tuple[bool, int]:
        """
        Deletes a document based on provided query
        """
        try:
            result = self.collection.delete_one(query, session=self.session)
            if result:
                return True, result.deleted_count
            else:
                return False, 0
        except Exception as e:
            Logger.error(f"Mongo exception: Failed to delete data by query {query} - {e}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to delete the data.") from e
    
    @Logger.generate
    def delete_all(self, _id: str, user_id: Optional[str] = None) -> Tuple[bool, int]:
        """
        Deletes all documents based on the provided MongoDB ID and optional user ID.
        """
        try:
            if user_id:
                Logger.info(f"Deleting data based on user_id", logger_instance=self.logger)
                result = self.collection.delete_many({"_id": ObjectId(_id), "user_id": user_id}, session=self.session)
            else:
                Logger.info(f"Deleting data based on id", logger_instance=self.logger)
                result = self.collection.delete_many({"_id": ObjectId(_id)}, session=self.session)
            if result:
                return True, result.deleted_count
            else:
                raise Exception(f"Got error while deleting all: id : {_id} and user_id: {user_id}")
        except Exception as e: 
            Logger.error(f"The Mongo exception occurred: Failed to delete all data based on id :{_id} and user_id :{user_id}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to delete all data based on user id.") from e

    @Logger.generate
    def delete_all_by_key_value(self, key: str, value: Any) -> Tuple[bool, int]:
        """
        Deletes all documents matching the given key-value pair.
        """
        try:
            Logger.info(f"Deleting all documents associated with {key}: {value}", logger_instance=self.logger)
            result = self.collection.delete_many({key: value}, session=self.session)
            if result:
                return True, result.deleted_count
            else:
                # Based on previous implementations, raising exception if no delete might be too aggressive if 0 is valid.
                # However, following the pattern of delete_all_by_chat_id which raised exception if result was falsy 
                # (though delete_many result is always truthy in pymongo unless something is wrong, wait, result.deleted_count is 0 if nothing deleted)
                # The original askedata code `if result:` checks if the object exists.
                # Let's return the count.
                return True, result.deleted_count
        except Exception as e:
            Logger.error(f"MongoException occurred while deleting data for {key}: {value}", exc_info=True, logger_instance=self.logger)
            raise MongoException(f"Failed to delete data for {key}: {value}.") from e


    def get_one_by_query(self, query: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Fetch a document from the collection based on the provided query.
        """
        try:
            Logger.info(f"Fetching data by query: {query}", logger_instance=self.logger)
            result = self.collection.find_one(query, session=self.session)
            if result:
                if '_id' in result:
                    result['_id'] = str(result['_id'])
                return True, result
            else:
                return False, {}
        except Exception as e:
            Logger.error(f"MongoFactory exception: {e}", exc_info=True, logger_instance=self.logger)
            raise MongoException("Failed to get data by query") from e
