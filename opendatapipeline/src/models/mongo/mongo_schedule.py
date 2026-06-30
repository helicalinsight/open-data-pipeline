
from bson import ObjectId
import os

from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError

from src.exceptions.exception import MongoException
from src.logger.logger import Logger, logger
from src.models.mongo.mongo_factory import MongoFactory

class MongoSchedule(MongoFactory): # pragma: no cover
    """
    A class for managing schedule-related data in a MongoDB collection. Inherits from MongoFactory.
    Provides methods for retrieving schedule data based on user ID and schedule ID.

    Attributes:
        collection (Collection): The MongoDB collection instance used for operations.
        session (Session): The MongoDB session used for database operations.

    Methods:
        get_all_by_chat_id_and_schedule_id(user_id, schedule_id): 
            Retrieves documents from the collection based on the provided user ID and schedule ID.

    Exceptions:
        MongoException: If an exception occurs while retrieving the data.
    """
    @Logger.generate
    def get_all_by_chat_id_and_schedule_id(self, user_id,schedule_id):
        """
        Retrieves documents from the collection based on the provided user ID and schedule ID.

        :param user_id: The ID of the user whose schedule data is to be fetched.
        :param schedule_id: The ID of the schedule to be retrieved, which should be in ObjectId format.
        :return: A tuple (success, result) where `success` is a boolean indicating whether the operation was successful,
                 and `result` contains the documents matching the query. If no documents are found, `result` will be empty.
        :raises MongoException: If an exception occurs while retrieving the data.
        """
        try:
            logger.info(f"Fetching data by user_id")
            query = {
                "user_id": user_id,
                "_id": ObjectId(schedule_id)
            }
            result=self.collection.find(query, session=self.session)
            if result:
                return True, result
            else:
                raise Exception(f"Got error while getting all schedules by user_id : {user_id} and schedule_id : {schedule_id}")
        except Exception as e: # pragma: no cover
            logger.error(f"The Mongo exception occurred: Failed to get the data with user_id :{user_id} and schedule_id :{schedule_id}", exc_info=True)
            raise MongoException("Failed to get the data.") from e