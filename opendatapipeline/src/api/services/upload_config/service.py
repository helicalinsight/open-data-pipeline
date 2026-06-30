from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory

from ....configurations.api.config import BaseConfig
from ....logger.logger import Logger, logger
from werkzeug.utils import secure_filename
from src.api.services.base.service_parent import ServiceParent
import os


class UploadConfigService(ServiceParent):
    
    def __init__(self,session=None):
        super().__init__(session)

    @Logger.generate
    def upload_config(self, file,db_name,user_id):
        """Uploads a configuration file to a specified location.

        Args:
            file (werkzeug.datastructures.FileStorage): The file to be uploaded.
            db_name (str): The name of the database associated with the configuration file.
            user_id (str): The ID of the user uploading the file.

        Returns:
            dict: A dictionary containing the success status and file details.
                - success (bool): Indicates whether the upload was successful.
                - user_id (str): The ID of the user who uploaded the file.
                - details (dict): Contains file details, including the path where the file is saved.

        Raises:
            Exception: If the file is not provided, or if there is an error during file saving.

        HTTP Status Codes:
            200: Upload was successful.
            500: Internal server error due to failure in uploading the file.
        """
        try:

            if not file:
                raise Exception("Please make sure you selected the files to upload.")

            user_folder_path = os.path.join(BaseConfig.BASE_DIR, BaseConfig.UPLOAD_FOLDER, user_id, "configurations", db_name)
            os.makedirs(user_folder_path, exist_ok=True)  # Create the folder if it doesn't exist

            filename = file.filename

            temp_save_path = os.path.join(user_folder_path, filename)
            file.save(temp_save_path)
            logger.info("Successfully performed upload config")
            return {
                "success": True,
                "user_id": user_id,
                "details": {"file": temp_save_path}
            }, 200

        except Exception as e: # pragma: no cover
            logger.error(f"{e}", exc_info=True)
            self._safe_abort_transaction()  
            return {
                "success": False,
                "msg": f"{e}"
                # "msg": "Unable to Upload."
            },500

