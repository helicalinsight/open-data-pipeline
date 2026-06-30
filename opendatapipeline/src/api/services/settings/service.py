from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ....logger.logger import Logger, logger
from src.api.services.base.service_parent import ServiceParent



class SettingsService(ServiceParent):
    """Service for managing user settings.

    This service provides functionality to retrieve, create, and update user settings.

    Attributes:
        session (Session): The database session used for operations.
        mongo_connector (MongoConnector): MongoDB connector instance.
        mongo_client (MongoClient): MongoDB client instance.
        user_collection (MongoFactory): Collection handler for user documents.

    Methods:
        get_settings(user_id):
            Retrieves the settings for a specified user.
        
        create_settings(user_id, data):
            Creates new settings for a specified user, with validation.
        
        update_settings(user_id, data):
            Updates existing settings for a specified user.
    """
    def __init__(self,session=None):
        """Initializes the SettingsService with a database session.

        Args:
            session (Session, optional): The database session to use for operations.
        """
        
        super().__init__(session)
        self.user_collection = MongoFactory(self.client, "users", session=self.session)

    
    @Logger.generate
    def get_settings(self, user_id):
        """Retrieves the settings for the specified user.

        Args:
            user_id (str): The ID of the user whose settings are to be fetched.

        Returns:
            dict: The settings of the specified user. Returns an empty dictionary if settings are not found.
        """
        settings = {}
        try:
            status, user_data = self.user_collection.get_by_id(user_id)
            if user_data:
                settings = user_data["settings"]
            logger.info("Successfully got the settings")
            return settings
        except Exception as e:
            logger.error(f"{e}", exc_info=True)
            return settings
    
    @Logger.generate
    def create_settings(self, user_id, data):
        """Creates new settings for the specified user with validation.
        
        Args:
            user_id (str): The ID of the user for whom settings are to be created.
            data (dict): The settings data to be created. Can include "files" with file_size and num_records.
            
        Returns:
            dict: The created settings for the user.
        """
        try:
            default_file_size = 5
            default_num_records = 100
            
            files_data = data.get("files", {})
            
            # Apply validation and defaults for file_size
            file_size = files_data.get("file_size")
            if file_size is None or str(file_size) in ["0", "0MB"]:
                file_size = default_file_size
                
            # Apply defaults for num_records if None
            num_records = files_data.get("num_records")
            if num_records is None:
                num_records = default_num_records
            
            # Create settings with validated values
            settings = {
                "files": {
                    "file_size": file_size,
                    "num_records": num_records
                }
            }
            
            # Update database
            self.user_collection.update_one(user_id, "settings", settings)
            
            status, user_data = self.user_collection.get_by_id(user_id)
            logger.info("Successfully created the settings")
            return user_data.get("settings", {})
            
        except Exception as e:
            logger.error(f"{e}", exc_info=True)
            self._safe_abort_transaction()  
            raise Exception(e) from e
