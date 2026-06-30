
import os
import csv 
from ....models.mongo.mongo_factory import MongoFactory
import uuid
from ....models.connector import MongoConnector
from ....configurations.api.config import BaseConfig
from ....exceptions.exception import *
from ....logger.logger import Logger, logger

mongo_connector = MongoConnector()
mongo_client = mongo_connector.client

class DataLoads:
    """
    The DataLoads class is designed for exporting data to a specified file path. 
    This class offers methods for exporting data in csv format. 
    In addition to the primary export method, it includes internal utility methods that support the export process
    """
    def __init__(self, session):
        self.session = session

    @Logger.generate
    def export(self, user_info, dataframe, parameters):
        """
        Exports the provided DataFrame to a CSV or excel file using the Pandas library. 
        This method handles the conversion of the DataFrame into a CSV format and writes it to the specified file path

        :param user_info: A dictionary containing user information, including user ID and chat ID
        :type user_info: dict
        :param dataframe: The dataframe to be exported to a CSV or excel file
        :type dataframe: pandas.DataFrame
        :param parameters: A dictionary which includes source ID and export name
        :type parameters: dict
        :return: The status of the export (True if successfull), the export ID, and the export name
        :rtype: bool, str, str
        """
        export_path = None
        id=None
        export_name=None
        try:
            user_id = user_info["user_id"]
            job_id = user_info["chat_id"]
            id=parameters['source']['source_id']
            export_name = f"{id}.csv" if "export_name" not in parameters else parameters["export_name"]

            # Extract format from file extension
            
            file_extension = os.path.splitext(export_name)[1].lower()
            
            # Map file extensions to export formats (CSV and Excel only)
            extension_to_format = {
                '.csv': 'csv',
                '.xlsx': 'excel',
                '.xls': 'excel'
            }
            
            export_format = extension_to_format.get(file_extension, 'csv')
            
            # Generate export path
            success, export_path = self.generate_export_path(user_id, job_id, export_name)
            
            # Export based on format (CSV or Excel only)
            if export_format == 'csv':
                dataframe.to_csv(export_path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
                
            elif export_format == 'excel':
                try:
                    # Simple direct export to Excel
                    dataframe.to_excel(export_path, index=False, engine='openpyxl')
                    
                    # Verify the file was created properly
                    if os.path.exists(export_path) and os.path.getsize(export_path) > 0:
                        logger.info(f"Excel file successfully created at {export_path}, size: {os.path.getsize(export_path)} bytes")
                    else:
                        raise Exception("Excel file was not created properly")
                        
                except ImportError:
                    logger.error("openpyxl not available, falling back to CSV")
                    csv_path = export_path.replace('.xlsx', '.csv').replace('.xls', '.csv')
                    dataframe.to_csv(csv_path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
                    export_path = csv_path
                    export_name = export_name.replace('.xlsx', '.csv').replace('.xls', '.csv')
                    
                except Exception as excel_error:
                    logger.error(f"Excel export failed: {str(excel_error)}, falling back to CSV")
                    csv_path = export_path.replace('.xlsx', '.csv').replace('.xls', '.csv')
                    dataframe.to_csv(csv_path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
                    export_path = csv_path
                    export_name = export_name.replace('.xlsx', '.csv').replace('.xls', '.csv')
        
            else:
                # Fallback to CSV for any other format
                logger.warning(f"Unsupported export format '{export_format}', defaulting to CSV")
                dataframe.to_csv(export_path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
                
            logger.info(f"Exporting file to {export_path}")
            cache = MongoFactory(mongo_client, "cache", session=self.session)
            _, _ = cache.update_one_by_fields(parameters["source"]["source_id"], job_id, user_id, "export_path", export_path)
            _, _ = cache.update_one_by_fields(parameters["source"]["source_id"], job_id, user_id, "export_name", export_name)
            return True,id,export_name
        except Exception as e: # pragma: no cover
            logger.error(f"Failed to export file: {str(e)}", exc_info=True)
            raise UtilsException("Failed to export the file.") from e

    @staticmethod
    @Logger.generate
    def generate_export_path(user_id, job_id, export_name):
        """
        Generates a file path for exporting data by incorporating the user ID, job ID, and export name into the file path. 
        This method constructs a structured and unique file path to ensure organized and consistent data storage.

        :param user_id: The unique identifier for the user
        :type user_id: str
        :param job_id: The unique identifier for the job or task associated with the export
        :type job_id: str
        :param export_name: The name to be used for the exported file
        :type export_name: str
        :return: A boolean indicating whether the operation was successful or failed, along with the generated file path for the export
        :rtype: bool, str
        """
        try:
            logger.info("Generating export path.")
            export_path = os.path.join(BaseConfig.BASE_DIR, BaseConfig.UPLOAD_FOLDER, user_id, ".cache", job_id, "export")
            if not os.path.exists(export_path):
                os.makedirs(export_path)
            path = f"{export_path}/{export_name}".replace('\\', '/')
            logger.info("Returning generated export path.")
            return True, path
        except Exception as e:
            logger.error(f"Failed to generate export path in 'generate_export_path': {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate export path.") from e

    @staticmethod
    @Logger.generate
    def update_history(step: int, status: bool, function: str, parameters: dict, output: dict = None) -> dict:
        """
        Updates the history log with details related to a specific step of the process. This method records relevant information about the step, 
        such as its status, step_id, step_number, function_name, parameters used for the process and output(optional)
        ensuring comprehensive tracking and documentation of the process.

        :param step: The number of the step being recorded.
        :type step: int
        :param status: The status of the step, indicating success or failure (e.g., True for PASS, False for FAIL).
        :type status: bool
        :param function: A description of the function or operation performed in the step.
        :type function: str
        :param parameters: A dictionary containing the parameters used in the step.
        :type parameters: dict
        :param output: (Optional) A dictionary containing the output generated by the step.
        :type output: dict, optional
        :return: A boolean indicating success or failure, A dictionary containing the details of the step, including a unique identifier.
        :rtype: bool, dict
        """
        try:
            logger.info("Updating the history.")
            step_id = str(uuid.uuid4())
            history_entry = {
                "id": step_id,
                "step": step,
                "status": "PASS" if status else "FAIL",
                "function": function,
                "parameters": parameters,
                "output": None
            }
            logger.info("Returning updated history entry.")
            return True, history_entry
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while updating history: {str(e)}", exc_info=True)
            raise UtilsException("Failed to update the history.") from e

    @Logger.generate
    def get_step_number(self, user_info: dict) -> int:
        """
        Retrieves the next available step number based on the provided user information. This method determines the appropriate step number in a sequence or workflow, ensuring that the process continues in the correct order for the specified user.

        :param user_info: A dictionary containing user details such as user ID, session ID, and chat ID.
        :type user_info: dict
        :return: A boolean indicating success or failure, The next step number.
        :rtype: bool, int
        """
        try:
            logger.info("Getting step number.")
            step_number = 0
            chats = MongoFactory(mongo_client, "chats", session=self.session)
            success, chat_document = chats.get_by_id(user_info["chat_id"])
            if not success:
                update_success, modified_count = chats.update_one(user_info["chat_id"], "history", [])
            success, chat_document = chats.get_by_id(user_info["chat_id"])
            history = chat_document.get("history", [])
            history = [item for item in history if item["step"] not in [ "export","export_table","step_export"]]
            if history:
                # Find the last step number from the "history" array
                step_numbers = [int(item["step"]) for item in history]
                if step_numbers:
                    step_number = max(step_numbers) + 1
            logger.info("Returning step number")
            return True, step_number
        except Exception as e: # pragma: no cover
            logger.error(f'An error occurred while getting step number: {str(e)}', exc_info=True)
            raise UtilsException("Failed to get step number.") from e

    @Logger.generate
    def save_history(self, user_info: dict, history: dict) -> None:
        """
        Saves the history entries associated with a specific user. This method records and stores details of past actions or events for the user, maintaining a comprehensive history of interactions and activities.

        :param user_info: A dictionary containing user details such as user ID, session ID, and chat ID.
        :type user_info: dict
        :param history: A dictionary containing the history entries to be saved.
        :type history: dict
        :return: A boolean indicating success or failure
        :rtype: bool
        """
        try:
            logger.info("Saving history.")
            chats = MongoFactory(mongo_client, "chats", session=self.session)
            success, chat_document = chats.get_by_id(user_info["chat_id"])
            append_success, modified_count = chats.append_one(user_info["chat_id"], "history", history)
            logger.info("Successfully saved history.")
            return True
        except Exception as e: # pragma: no cover
            logger.error(f'An error occurred while saving history: {str(e)}', exc_info=True)
            raise UtilsException("Failed to save the history.") from e
