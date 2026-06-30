import json
import os
from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

from ...configurations.api.config import BaseConfig
from ...configurations.user_config.config import settings


from ...models.connector import MongoConnector

import logging
logging.basicConfig(level=logging.DEBUG)
mongo_connector = MongoConnector()
mongo_client = mongo_connector.client
class Users: # pragma: no cover
    """
    A class to represent a user in the system. Manages user creation, updates, and retrieval operations.

    Attributes:
        _id (str): The unique identifier for the user, assigned after saving.
        google_id (str): The user's Google ID.
        email (str): The user's email address.
        verified_email (str): Whether the user's email is verified (default empty string).
        name (str): The user's full name (default empty string).
        given_name (str): The user's given name (default empty string).
        family_name (str): The user's family name (default empty string).
        picture (str): The URL to the user's profile picture (default empty string).
        locale (str): The user's locale (default empty string).
        external (str): Indicates if the user is external (default empty string).
        password (str): The user's password (default empty string).
        jwt_auth_active (bool): Indicates whether JWT authentication is active (default False).
        date_joined (datetime): The date and time when the user joined.
        role (str): The user's role (default is "free").
        session: The MongoDB session to be used for database operations.

    :param req_data: A dictionary containing user data.
    :type req_data: dict
    :param session: The MongoDB session to be used for database operations.
    :type session: pymongo.client_session.ClientSession
    """
    def __init__(self, req_data, session):
        """
        Initializes a Users instance with provided request data and MongoDB session.

        :param req_data: A dictionary containing user data.
        :type req_data: dict
        :param session: The MongoDB session to be used for database operations.
        :type session: pymongo.client_session.ClientSession
        """
        self._id = None
        self.google_id = req_data.get("id")
        self.email = req_data.get("email")
        self.verified_email = req_data.get("verified_email","")
        self.name = req_data.get("name","")
        self.given_name = req_data.get("name","")
        self.family_name = req_data.get("family_name","")
        self.picture = req_data.get("picture","")
        self.locale = req_data.get("locale","")
        self.external = req_data.get("external","")
        self.password = req_data.get("password","")
        self.jwt_auth_active = False
        self.date_joined = datetime.utcnow()
        self.role="free"
        self.session = session

    def save(self):
        """
        Saves the user data to the MongoDB collection. Creates a new user document.

        :return: None
        :rtype: None
        """
        user_data = {
            "email": self.email,
            "name": self.name,
            "given_name": self.given_name,
            "family_name": self.family_name,
            "picture": self.picture,
            "locale": self.locale,
            "external": self.external,
            "password": self.password,
            "jwt_auth_active": self.jwt_auth_active,
            "date_joined": self.date_joined,
            "role":self.role,
            "settings":settings
        }

        result = mongo_client.users.insert_one(user_data)
        self._id =str(result.inserted_id)

    def setup(self):
        """
        Sets up the user's environment by creating default chat, file records, and necessary folders.

        :return: None
        :rtype: None
        """
        logging.info("Starting Setting Up")
        # Add the new chat to the user's document
        default_chat = mongo_client.chats.insert_one({
            "user_id": self._id,
            "chat_name": "default_chat",
            "default": True
        })
        default_files = mongo_client.files.insert_one({
            "user_id": self._id,
            "files": []
        })
        user_folder_path = os.path.join(BaseConfig.BASE_DIR, BaseConfig.UPLOAD_FOLDER, str(self._id))
        os.makedirs(user_folder_path, exist_ok=True)
        files_folder_path = os.path.join(user_folder_path, "sources")
        os.makedirs(files_folder_path, exist_ok=True)
        sample_folder_path = os.path.join(user_folder_path, ".sample")
        os.makedirs(sample_folder_path, exist_ok=True)
        cache_folder_path = os.path.join(user_folder_path, ".cache")
        os.makedirs(cache_folder_path, exist_ok=True)
        chats_folder = os.path.join(cache_folder_path,str(default_chat.inserted_id))
        os.makedirs(chats_folder,exist_ok=True)


    def set_password(self, password):
        """
        Sets the user's password, hashing it before storage.

        :param password: The plaintext password to be hashed and set.
        :type password: str
        :return: None
        :rtype: None
        """
        if password is not None:
            self.password = generate_password_hash(password)

    def check_password(self,hashedPassword, password):
        """
        Checks if the provided plaintext password matches the stored hashed password.

        :param hashedPassword: The hashed password stored in the database.
        :type hashedPassword: str
        :param password: The plaintext password to be checked.
        :type password: str
        :return: True if the password matches, False otherwise.
        :rtype: bool
        """
        if password is not None:
            return check_password_hash(hashedPassword, password)

    def update_email(self, new_email):
        """
        Updates the user's email address.

        :param new_email: The new email address to be set.
        :type new_email: str
        :return: None
        :rtype: None
        """
        self.email = new_email

    def update_username(self, new_username):
        """
        Updates the user's full name.

        :param new_username: The new full name to be set.
        :type new_username: str
        :return: None
        :rtype: None
        """
        self.name = new_username

    def check_jwt_auth_active(self):
        """
        Checks if JWT authentication is active for the user.

        :return: True if JWT authentication is active, False otherwise.
        :rtype: bool
        """
        return self.jwt_auth_active

    def set_jwt_auth_active(self, set_status):
        """
        Sets the status of JWT authentication for the user.

        :param set_status: The status to be set (True or False).
        :type set_status: bool
        :return: None
        :rtype: None
        """
        self.jwt_auth_active = set_status

    @classmethod
    def get_by_id(cls, google_id):
        """
        Retrieves user data by Google ID.

        :param google_id: The Google ID of the user.
        :type google_id: str
        :return: The user data if found, None otherwise.
        :rtype: dict or None
        """

        user_data = mongo_client.users.find_one({"google_id": google_id})

        if user_data:
            return user_data
        return None



    @classmethod
    def get_by_email(cls, email):
        """
        Retrieves user data by email address.

        :param email: The email address of the user.
        :type email: str
        :return: The user data if found, None otherwise.
        :rtype: dict or None
        """
        user_data = mongo_client.users.find_one({"email": email})
        if user_data:
            return user_data
        return None
    
    @classmethod
    def get_by_user_id(cls, user_id):
        """
        Retrieves user data by user_id 

        :param user_id: The user_id 
        :type user_id: str
        :return: The user data if found, None otherwise.
        :rtype: dict or None
        """
        try:
            user_data = mongo_client.users.find_one({"_id" : ObjectId(user_id)})
            if user_data:
                return user_data
        except Exception as e: # pragma: no cover
            return e

    @classmethod
    def delete_api_key(cls, user_id):
        """
        Removes api_key, token_name, and api_key_expiry_date from a user's document .

        :param user_id: The unique identifier of the user.
        :type user_id: str
        :return: result
        :rtype: dict
        """
        try:
            result = mongo_client.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$unset": {"api_key": "", "token_name": "", "api_key_expiry_date": ""}}
            )
            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def get_by_name(cls, name):
        """
        Retrieves user data by full name.

        :param name: The full name of the user.
        :type name: str
        :return: The user data if found, None otherwise.
        :rtype: dict or None
        """
        user_data = mongo_client.users.find_one({"name": name})
        if user_data:
            return user_data
        return None

    def to_dict(self):
        """
        Converts the user data to a dictionary format.

        :return: A dictionary containing user data.
        :rtype: dict
        """
        return {
            "id": self._id,
            "name": self.name,
            "email": self.email
        }

    def to_json(self):
        """
        Converts the user data to a JSON string.

        :return: A JSON string containing user data.
        :rtype: str
        """
        return json.dumps(self.to_dict())
