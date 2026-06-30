
from .mongo_factory import MongoFactory
from ...exceptions.exception import MongoException
from ...logger.logger import Logger, logger
from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError

class MongoFiles(MongoFactory): # pragma: no cover
    """
    A class for managing files in a MongoDB collection. Inherits from MongoFactory.
    Provides methods for fetching, updating, and deleting file information.
    """
    @Logger.generate
    def get_by_file_id(self, user_id, file_id):
        """
        Retrieves a file from the `files` array based on the user ID and file ID.
        
        :param user_id: The ID of the user whose files are to be searched.
        :param file_id: The ID of the file to retrieve.
        :return: A tuple (success_flag, file_info). `file_info` is the dictionary of the file details.
        :raises MongoException: If the file could not be retrieved.
        """
        try:
            logger.info("get_by_file_id started.")
            pipeline = [
                {"$match": {"user_id": user_id, "files.file_id": file_id}},
                {"$project": {"_id": 0, "files": {"$filter": {
                    "input": "$files",
                    "as": "file",
                    "cond": {"$eq": ["$$file.file_id", file_id]}
                }}}}
            ]

            result = self.collection.aggregate(pipeline, session=self.session)
            if result:
                file_info = next(result, {}).get("files", [])[0]
                logger.info("Fetched details successfully.")
                return True, file_info
            else:
                raise Exception(f"Got error while getting file by id: user_id : {user_id} and file_id : {file_id}")
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to get details by user_id :{user_id} and file_id :{file_id}", exc_info=True)
            raise MongoException("Failed to get details by file id.") from e



    @Logger.generate
    def is_file_exist(self,user_id, file_name):
        """
        Checks if a file exists in the `files` array based on the user ID and file name.
        
        :param user_id: The ID of the user whose files are to be searched.
        :param file_name: The name of the file to check for existence.
        :return: A tuple (success_flag, file_info). `file_info` is the dictionary of the file details, or None if not found.
        """
        try:
            logger.info("get_by_file_id started.")
            pipeline = [
                {"$match": {"user_id": user_id, "files.file_name": file_name}},
                {"$project": {"_id": 0, "files": {"$filter": {
                    "input": "$files",
                    "as": "file",
                    "cond": {"$eq": ["$$file.file_name", file_name]}
                }}}}
            ]
            result = self.collection.aggregate(pipeline)
            if result:
                file_info = next(result, {}).get("files", [])[0]
                return True, file_info
            else:
                return None,None
            
        except OperationFailure as e:
            raise OperationFailure(e)
        except Exception as e: # pragma: no cover
            
            logger.error(f"The Mongo exception occurred: File does not exists with user_id :{user_id} and file_name :{file_name}", exc_info=True)
            return None,None

    @Logger.generate
    def update_by_file_id(self, user_id, file_id, update_info):
        """
        Updates the details of a file in the `files` array based on user ID and file ID.
        
        :param user_id: The ID of the user whose file is to be updated.
        :param file_id: The ID of the file to be updated.
        :param update_info: A dictionary of fields to update with their new values.
        :return: A tuple (success_flag, modified_count). `modified_count` is the number of documents modified.
        :raises MongoException: If the file could not be updated.
        """
        try:
            logger.info(f" update_by_file_id started.")
            query = {
                "user_id": user_id,
                "files.file_id": file_id
            }

            update = {"$set": {}}

            for key, value in update_info.items():
                update["$set"]["files.$." + key] = value

            result = self.collection.update_one(query, update, session=self.session)
            if result:
                return True, result.modified_count
            else:
                raise Exception(f"Got error while updating file by id: user_id : {user_id}, file_id : {file_id} and update_info : {update_info}")
        except OperationFailure as e:
            raise OperationFailure(e)
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred at updating file information with user_id :{user_id}, file_id :{file_id} and update_info :{update_info}", exc_info=True)
            raise MongoException("Could not fetch the details.") from e

    @Logger.generate
    def delete_by_file_id(self, user_id, file_id):
        """
        Removes a file from the `files` array based on user ID and file ID.
        
        :param user_id: The ID of the user whose file is to be deleted.
        :param file_id: The ID of the file to be deleted.
        :return: A tuple (success_flag, modified_count). `modified_count` is the number of documents modified.
        :raises MongoException: If the file could not be deleted.
        """

        try:
            query = {
                "user_id": user_id,
                "files.file_id": file_id
            }

            update = {
                "$pull": {
                    "files": {
                        "file_id": file_id
                    }
                }
            }

            result = self.collection.update_one(query, update, session=self.session)
            if result:
                return True, result.modified_count
            else:
                raise Exception(f"Got error while deleting file by id: user_id : {user_id} and file_id : {file_id}")

        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Error deleting file with user_id :{user_id} and file_id :{file_id}", exc_info=True)
            raise MongoException("Error deleting file with ID") from e
        
        
    @Logger.generate
    def get_by_file_id_only(self, file_id):
        """
        Retrieves a file from the `files` array based on the file ID only.
        
        :param file_id: The ID of the file to retrieve.
        :return: A tuple (success_flag, file_info). `file_info` is the dictionary of the file details.
        :raises MongoException: If the file could not be retrieved.
        """
        try:
            logger.info("get_by_file_id_only started.")
            pipeline = [
                {"$match": {"files.file_id": file_id}},
                {"$project": {"_id": 0, "files": {"$filter": {
                    "input": "$files",
                    "as": "file",
                    "cond": {"$eq": ["$$file.file_id", file_id]}
                }}}}
            ]

            result = self.collection.aggregate(pipeline, session=self.session)
            if result:
                file_info = next(result, {}).get("files", [])[0]
                logger.info("Fetched details successfully.")
                return True, file_info
            else:
                raise Exception(f"Got error while getting file by id only: file_id : {file_id}")
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to get details by file_id :{file_id}", exc_info=True)
            raise MongoException("Failed to get details by file id.") from e