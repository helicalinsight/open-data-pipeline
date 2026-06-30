import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from ...configurations.api.config import BaseConfig
from ...configurations.user_config.config import settings

from ...logger.logger import Logger, logger
from ...models.connector import MongoConnector


class GoogleUsers: # pragma: no cover
    """
    A class to represent a user in the system using Google authentication data. 
    Manages user creation, updates, and retrieval, and handles user-related operations.

    Attributes:
        _id (str): The unique identifier for the user, assigned after saving.
        google_id (str): The user's Google ID.
        email (str): The user's email address.
        verified_email (bool): Whether the user's email is verified.
        name (str): The user's full name.
        given_name (str): The user's given name.
        family_name (str): The user's family name.
        picture (str): The URL to the user's profile picture.
        locale (str): The user's locale.
        external (bool): Whether the user is external.
        password (str): The user's password (hashed).
        jwt_auth_active (bool): Indicates whether JWT authentication is active.
        date_joined (datetime): The date and time when the user joined.
        role (str): The user's role (default is "free").
        mongo_connector (MongoConnector): The MongoDB connector instance.
        mongo_client (MongoClient): The MongoDB client instance.
        session (Session): The MongoDB session.

    Methods:
        __init__(req_data, session): Initializes a GoogleUsers instance with provided request data and MongoDB session.
        save(): Saves the user data to the MongoDB collection. Creates a new user document.
        setup(): Sets up the user's environment by creating default chat, file records, and necessary folders.
        set_password(password): Sets the user's password, hashing it before storage.
        check_password(password): Checks if the provided plaintext password matches the stored hashed password.
        update_email(new_email): Updates the user's email address.
        update_username(new_username): Updates the user's full name.
        check_jwt_auth_active(): Checks if JWT authentication is active for the user.
        set_jwt_auth_active(set_status): Sets the status of JWT authentication for the user.
        get_by_id(google_id): Retrieves user data by Google ID.
        get_by_email(email): Retrieves user data by email address.
        get_by_name(name): Retrieves user data by full name.
        to_dict(): Converts the user data to a dictionary format.
        to_json(): Converts the user data to a JSON string.
    """
    def __init__(self, req_data, session):
        """
        Initializes a GoogleUsers instance with provided request data and MongoDB session.

        :param req_data: A dictionary containing user data from Google authentication.
        :param session: The MongoDB session to be used for database operations.
        """
        self._id = None
        self.google_id = req_data.get("id")
        self.email = req_data.get("email")
        self.verified_email = req_data.get("verified_email")
        self.name = req_data.get("name")
        self.given_name = req_data.get("given_name")
        self.family_name = req_data.get("family_name")
        self.picture = req_data.get("picture")
        self.locale = req_data.get("locale")
        self.external = req_data.get("external")
        self.password = req_data.get("password")
        self.jwt_auth_active = False
        self.date_joined = datetime.utcnow()
        self.role="free"
        self.mongo_connector = MongoConnector()
        self.mongo_client = self.mongo_connector.client
        self.session = session

    def save(self):
        """
        Saves the user data to the MongoDB collection. Creates a new user document.

        :return: None
        """
        user_data = {
            "google_id": self.google_id,
            "email": self.email,
            "verified_email": self.verified_email,
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

        result = self.mongo_client.users.insert_one(user_data)
        self._id =str(result.inserted_id)
        logger.info(f"user created id: {self._id}")

    def setup(self):
        """
        Sets up the user's environment by creating default chat, file records, and necessary folders.

        :return: None
        """
        logger.info("Starting Setting Up")
        # Add the new chat to the user's document
        default_chat = self.mongo_client.chats.insert_one({
            "user_id": self._id,
            "chat_name": "default_chat",
            "default": True
        })
        default_files = self.mongo_client.files.insert_one({
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
        logger.info("setup complete..")


    def set_password(self, password):
        """
        Sets the user's password, hashing it before storage.

        :param password: The plaintext password to be hashed and set.
        :return: None
        """
        if password is not None:
            self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        Checks if the provided plaintext password matches the stored hashed password.

        :param password: The plaintext password to be checked.
        :return: True if the password matches, False otherwise.
        """
        if password is not None:
            return check_password_hash(self.password, password)

    def update_email(self, new_email):
        """
        Updates the user's email address.

        :param new_email: The new email address to be set.
        :return: None
        """
        self.email = new_email

    def update_username(self, new_username):
        """
        Updates the user's full name.

        :param new_username: The new full name to be set.
        :return: None
        """
        self.name = new_username

    def check_jwt_auth_active(self):
        """
        Checks if JWT authentication is active for the user.

        :return: True if JWT authentication is active, False otherwise.
        """
        return self.jwt_auth_active

    def set_jwt_auth_active(self, set_status):
        """
        Sets the status of JWT authentication for the user.

        :param set_status: The status to be set (True or False).
        :return: None
        """
        self.jwt_auth_active = set_status

    def get_by_id(self, google_id):
        """
        Retrieves user data by Google ID.

        :param google_id: The Google ID of the user.
        :return: The user data if found, None otherwise.
        """

        user_data = self.mongo_client.users.find_one({"google_id": google_id})

        if user_data:
            return user_data
        return None



    def get_by_email(self, email):
        """
        Retrieves user data by email address.

        :param email: The email address of the user.
        :return: The user data if found, None otherwise.
        """
        user_data = self.mongo_client.users.find_one({"email": email})
        if user_data:
            return user_data
        return None

    def get_by_name(self, name):
        """
        Retrieves user data by full name.

        :param name: The full name of the user.
        :return: The user data if found, None otherwise.
        """
        user_data = self.mongo_client.users.find_one({"name": name})
        if user_data:
            return user_data
        return None

    def to_dict(self):
        """
        Converts the user data to a dictionary format.

        :return: A dictionary containing user data.
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
        """
        return json.dumps(self.to_dict())
