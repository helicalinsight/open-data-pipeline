from .mongo_factory import MongoFactory
from ..connector import MongoConnector
from datetime import datetime
import random
import time


mongo_connector = MongoConnector()
mongo_client = mongo_connector.client

random_messages = [
    "Hello!",
    "How are you?",
    "What can I do for you?",
    "Nice to meet you!",
    "Have a great day!",
    "Goodbye!",
]

class MongoLangchain(MongoFactory): # pragma: no cover
    """
    A class for managing chat-related data in a MongoDB collection. Inherits from MongoFactory.
    Provides methods for finding documents and creating or updating chat messages.
    """
    def find_one(self, query):
        """
        Finds a single document in the collection that matches the given query.

        :param query: A dictionary representing the query to match documents.
        :return: The first document that matches the query, or None if no document matches.
        """
        return self.collection.find_one(query, session=self.session)
    
    def create_or_update(self, data):
        """
        Creates a new document or updates an existing one based on the provided data.
        
        - If a document with the specified `user_id` and `chat_id` exists, it updates the `messages` array by adding the new message.
        - If no such document exists, it inserts a new document with the given `user_id`, `chat_id`, and the initial message.

        :param data: A dictionary containing the following keys:
            - "user_id": The ID of the user.
            - "chat_id": The ID of the chat.
            - "messages": A list of messages, where the first element is the message to be added.
        :return: None
        """
        user_id = data.get("user_id")
        chat_id = data.get("chat_id")


        existing_document = self.collection.find_one({"user_id": user_id, "chat_id": chat_id}, session=self.session)

        # existing_document = self.collection.find_one({"user_id": user_id, "chat_id": chat_id})
        if existing_document:
            # Document exists, update the messages array
            if len(data.get("messages"))==0:
                    pass
            else:
                self.collection.update_one(
                    {"user_id": user_id, "chat_id": chat_id},
                    {"$push": {"messages": data.get("messages")[0]}},
                    session=self.session
                )

        else:
            
            # Document does not exist, insert a new document
            if len(data.get("messages"))==0:
                self.collection.insert_one({
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "messages": []
                }, session=self.session)
            else:
                self.collection.insert_one({
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "messages": [data.get("messages")[0]]
                }, session=self.session)
