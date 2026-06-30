# from .process.processor import Processor
import uuid

from ...models.mongo.mongo_factory import MongoFactory

from ..metadata.meta_processor import MetaProcessor
import random
import string
from ..transfrom.data_summary.data_summary import DataSummary
from ...models.connector import MongoConnector
from ...models.mongo.mongo_files import MongoFiles
from ...configurations.api.config import BaseConfig
from ...logger.logger import Logger, logger
from ...exceptions.exception import *
from ...api.services.rerun.utils import CreateDFDictionary
from ...api.services.rerun.service import ReRunService
from .transformations_utilities.utilities import TransformerUtilities

mongo_connector = MongoConnector()
mongo_client = mongo_connector.client

class Manager:
    """
    The Manager class is designed to handle various operations related to data management and processing. 
    It provides several methods for managing operations, exporting data, previewing results, updating 
    history, saving history and utility related method to get step number
    """
    def __init__(self, session):
        from .process.processor import Processor
        self.session = session
        self.processor = Processor(self.session)
        self.meta_processor = MetaProcessor(session=self.session)
        self.chats_collection = MongoFactory(mongo_client, "chats", session=self.session)
        self.dataframe_configuration = None

    @Logger.generate
    def manage_operation(self, user_info: dict, intent_name: str, parameters: dict) -> tuple:
        """
        This method manages the execution of a specified intent operation, updates the operation history, and saves the updated history. It coordinates the execution of the operation based on the provided intent and associated data, ensuring that the history of operations is accurately recorded and preserved

        :param user_info: The details of the user like user_id, chat id
        :type user_info: dict
        :param intent_name: The name of the intent or operation to execute
        :type intent_name: str
        :param parameters: Has source_id associated with the user
        :type parameters: dict
        :return:  A boolean indicating success or failure, metadata_status, load, msg, The details of error
        :rtype: bool, bool, dict, str, dict
        """
        try:
            success, chat_item = self.chats_collection.get_by_id(user_info['chat_id'])
            self.dataframe_configuration = CreateDFDictionary(self.session).create(user_info["chat_id"])
            self.dataframe_configuration["type"] = "LLM" if intent_name=="pytool" else None # TODO: This is error prone. At various places, we expecte dataframe_config to have each item as a dictionary
            output = None
            execution_type = "default"
            load = {"success": False, "source_id": None}
            if intent_name in ["union", "joins"]:
                execution_type = "joins_unions"
                parameters["dataframe_aliases"] = [self.dataframe_configuration[s_id]["alias"] for s_id in parameters.get("source_id")]
            else:
                if not parameters.get('source_id'):
                    parameters['source_id'] = chat_item.get("cwf", {}).get("source_id")
                parameters["dataframe_alias"] = self.dataframe_configuration[parameters.get("source_id")]["alias"]
            status, metadata_status, df, msg, new_df, details = self.processor.execute_operations(
                    intent_name, parameters,user_info=user_info, execution_type=execution_type, dataframe_configuration=self.dataframe_configuration)
            logger.info(f"status, metadata_status, df, msg, new_df, details {status, metadata_status, df, msg, new_df, details}")
            if metadata_status:
                if new_df:
                    df_dict = CreateDFDictionary(self.session).create(user_info["chat_id"])
                    file_name = TransformerUtilities().generate_alias(df_dict, f"df_{intent_name}")
                    user_info["file_name"] = file_name
                    user_info["type"] = "csv"
                    user_info["intent"] = intent_name
                    success ,_source_id =self.meta_processor.generate(df,**user_info)
                    if success:
                        load = {"success": success, "files": [{"source_id": _source_id, "alias": file_name, "type": "csv"}]}
                        output = {"source_id": _source_id, "dataframe_alias": file_name}
                else:
                    self.meta_processor.update(
                        parameters["source_id"], df, user_info["chat_id"], user_info["user_id"])
            
            if intent_name=="pytool":
                output = details.get("new_ids")
            parameters.pop('df', None)
            parameters.pop('df_alias', None)
            # NOTE: df_info is discarded here because PyTool independently fetches 
            # dataframes from the backend pipeline instead of relying on this object.
            parameters.pop('df_info', None)
            success, history = self.update_history(status=status, function=intent_name,
                                        parameters=parameters, output=output)
            logger.info(f"history {history}")
            self.save_history(user_info, history)
            logger.info(f"status, metadata_status, load, msg, details {status, metadata_status, load, msg, details}")
            return status, metadata_status, load, msg, details
        except Exception as e: # pragma: no cover
            raise ManagerException(e) from e

    @Logger.generate
    def manage_export(self, user_info: dict, intent_name: str, parameters: dict):
       """
       This method executes an export operation, sending data to the specified destination in the given format. 
       It handles the process of exporting data, ensuring that it is correctly formatted and transmitted to 
       the desired location and returns the export name and its id

       :param user_info: The details of the user like user_id, chat id
       :type user_info: dict
       :param intent_name: The name of the intent or operation to execute
       :type intent_name: str
       :param parameters: Has source_id associated with the user
       :type parameters: dict
       :return:  A boolean indicating success or failure, The export id, The export name
       :rtype: bool, str, str
       """
       try:
            success, id, export_name = self.processor.execute_export(user_info,intent_name, parameters)
            succc, history = self.update_history(success, intent_name, parameters)
            self.save_history(user_info, history)
            return success, id, export_name
       except Exception as e: 
            logger.error(f"An error occurred in 'manage_export' function with user_info: {user_info}, intent_name :{intent_name} and parameters :{parameters}", exc_info=True)
            raise ManagerException(e) from e
       
    @Logger.generate
    def preview(self, source_id: str, alias: str, chat_id: str = None) -> str:
        """
        This method reads a Feather file identified by the provided source_id and generates a detailed preview of the resulting DataFrame. The preview includes metadata such as column names, the number of rows, and additional information about the DataFrame

        :param source_id: The ID of the Feather file
        :type source_id: str
        :param alias: The alias name associated with feather id
        :type alias: str
        :return: The preview info dictionary
        :rtype: dict
        """
        try:
            logger.info("Preview in manager is called.")
            _, chat_doc = self.chats_collection.get_by_id(chat_id)
            success, preview_info = self.processor.preview(source_id, alias, chat_id=chat_id, user_id=chat_doc['user_id'])
            logger.info("Successfully completed preview in manager.")
            return preview_info
        except Exception as e: 
            logger.error(f"An error occurred in 'preview' function with source_id: {source_id} and alias :{alias}", exc_info=True)
            raise ManagerException("Failed to preview.") from e
    
    @Logger.generate
    def yaml_preview(self, chat_id):
        """
        This method reads the pipeline using chat_id and generated preview based on yaml last step.
        :param chat_id: The ID of the chat_doc
        :type chat_id: str
        :return: The preview info dictionary
        :rtype: dict
        """
        try:
            logger.info("Preview in manager is called.")
            success, chat_item = self.chats_collection.get_by_id(chat_id)
            source_id = chat_item.get("cwf", {}).get("source_id")
            if source_id is None:
                return []
            source_id, data_dict = ReRunService(self.session).run_and_return_last_df(source_id, chat_id, chat_item.get("history"))
            if data_dict is None:
                return []
            alias = data_dict.get("alias")
            success, preview_info = self.processor.preview(source_id, alias, data_dict.get("df"))
            logger.info("Successfully completed preview in manager.")
            return preview_info
        except Exception as e:
            logger.error(f"An error occurred in 'yaml_preview' function with chat_id: {chat_id}", exc_info=True)
            raise ManagerException("Failed to preview.") from e

    @Logger.generate
    def update_history(self, status: str, function: str, parameters: dict, output: dict = None) -> dict:
        """
        This method updates the operation history with details of a specific step. 
        It records the provided step details, including function or operation performed, 
        and results, to maintain an accurate and comprehensive history of operations

        :param status: The status of the step - PASS or FAIL
        :type status: str
        :param function: The function or operation performed in the step
        :type function: str
        :param parameters: A dictionary containing the parameters used in the step
        :type parameters: dict
        :param output: The output generated by the step
        :type output: dict, optional
        :return:  A boolean indicating success or failure, The updated history entry
        :rtype: bool, dict
        """
        try:
            step_id = str(uuid.uuid4())
            history_entry = {
                "id": step_id,
                # "step": step,
                "status": "PASS" if status else "FAIL",
                "function": function,
                "parameters": parameters,
                "output": output
            }
            if function.lower() in ['joins', 'union']:
                history_entry['output'] = output
            return True, history_entry
        except Exception as e: # pragma: no cover
            logger.error(f"Manager Exception in 'update_history' with status: {status}, function :{function}, parameters :{parameters} and output :{output}", exc_info=True)
            raise UtilsException("Failed to update the history.") from e

    @Logger.generate
    def get_step_number(self, user_info: dict) -> int:
        """
        This method retrieves the next available step number in a sequence. 
        It is typically used to determine the appropriate number for the upcoming step in a series of 
        operations or processes, ensuring that each step is assigned a unique and sequential number

        :param user_info: A dictionary containing user ID, session ID and chat ID
        :type user_info: dict
        :return:  A boolean indicating success or failure, The next step number
        :rtype: bool, dict
        """
        try:
            step_number = 0
            chats = MongoFactory(mongo_client, "chats", session=self.session)
            get_status, chat_document = chats.get_by_id(user_info["chat_id"])
            if not get_status:
                update_success, modified_count = chats.update_one(user_info["chat_id"], "history", [])
            get_status, chat_document = chats.get_by_id(user_info["chat_id"])
            history = chat_document.get("history", [])
            
            if history:
                # Find the last step number from the "history" array
                history = [item for item in history if item["step"] not in [ "export","export_table","step_export"]]
                step_numbers = [int(item["step"]) for item in history]
                if step_numbers:
                    step_number = max(step_numbers) + 1
            return True, step_number
        except Exception as e: # pragma: no cover
            logger.error(f"Operation 'get_step_number' completed with exception: user_info :{user_info}", exc_info=True)
            raise UtilsException("Failed to get step number.") from e

    @Logger.generate
    def save_history(self, user_info: dict, history: dict) -> None:
        """
        This method saves the operation history along with user information to a specified storage medium. 
        It records details about the user and the operation history to ensure that all relevant data is preserved

        :param user_info: The user information which has unique id for the chat chat_id
        :type user_info: dict
        :param history: A dictionary containing the history entries to be saved
        :type history: dict
        :return: A boolean indicating success or failure
        :rtype: bool
        """
        try:
            chats = MongoFactory(mongo_client, "chats", session=self.session)
            chats.append_one(user_info["chat_id"], "history", history)
            return True
        except Exception as e: # pragma: no cover
            logger.error(f"Utils Exception in 'save_history' with user_info :{user_info} and history :{history}", exc_info=True)
            raise UtilsException("Failed to save history.") from e
