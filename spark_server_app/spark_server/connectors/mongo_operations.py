from bson import ObjectId
from ..connectors.connector import Connector
from ..logger.logger import Logger
from .secrets import secrets



log = Logger





from .connector import MongoConnector


class MongoOperations:

    def __init__(self):
        self.connector = MongoConnector()
        self.db = self.connector.client

    @log.generate
    def get_history_chat_and_user(self, chat_id, user_id):
        try:
            chat_document = self.db.chats.find_one({"user_id": user_id, "_id": ObjectId(chat_id)})
            if chat_document:
                chat_history = chat_document.get("history", [])
                return chat_history if chat_history else None
        except Exception as e:
            log.error(f"Error getting data from MongoDB: {e}")
            return None

    @log.generate
    def get_filepath_by_file_and_user_id(self, user_id, file_id):
        try:
            files_document = self.db.files.find_one({"user_id": user_id, "files.file_id": file_id},
                                                    {"files.$": 1})
            if files_document:
                file_object = files_document.get("files", [])[0]
                return file_object.get("file_path") if file_object else None
            else:
                return None
        except Exception as e:
            log.error(f"Error getting data: {e}")
            return None

    @log.generate
    def get_filetype_by_file_and_user_id(self, user_id, file_id):
        try:
            files_document = self.db.files.find_one({"user_id": user_id, "files.file_id": file_id},
                                                    {"files.$": 1})
            if files_document:
                file_object = files_document.get("files", [])[0]
                return file_object.get("file_type") if file_object else None
            else:
                return None
        except Exception as e:
            log.error(f"Error getting data: {e}")
            return None

    def get_connection_details(self, connection_id):
        try:
            connection_document = self.db.connections.find_one({"_id": ObjectId(connection_id)})
            if connection_document:
                connection_details = connection_document.get("connection_details", [])
                return connection_details if connection_details else None
        except Exception as e:
            log.error(f"Error getting data from MongoDB: {e}")
            return None

    def get_connection_type(self, connection_id):
        try:
            connection_document = self.db.connections.find_one({"_id": ObjectId(connection_id)})
            if connection_document:
                connection_type = connection_document.get("type")
                return connection_type if connection_type else None
        except Exception as e:
            log.error(f"Error getting data from MongoDB: {e}")
            return None
