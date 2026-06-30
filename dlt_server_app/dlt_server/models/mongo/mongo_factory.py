
from bson import ObjectId
from ...logger.logger import Logger, logger
from ...exceptions.exceptions import *
logger = Logger

from core.mongo.mongo_factory import MongoFactory as CoreMongoFactory

class MongoFactory(CoreMongoFactory):
    def __init__(self, mongo, collection_name):
        # Initialize core factory with session=None
        super().__init__(mongo, collection_name, session=None, logger=logger)
