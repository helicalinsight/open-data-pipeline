import os
import random

from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase
from ..extract.file_operations.read import Read
from ..metadata.file_operations.write import Write
from ..metadata.metadata import Metadata
from ..metadata.data_profile import DataProfile
import re
from ...models.mongo.mongo_factory import MongoFactory
from ...models.mongo.mongo_files import MongoFiles
import configparser
import uuid
from ...models.connector import MongoConnector
from ...configurations.api.config import BaseConfig
from ...hooks.database_connector import DatabaseConnector
from ...exceptions.exception import *
from ...api.data.chat import Chat
from ...api.data.cache import Cache
from ...logger.logger import Logger, logger
from ...utilities.utilities import CommonUtils
from ...api.services.pyspark_service.llm_chatbot import LLMChatBot
from ...api.services.pyspark_service.chat_memory import ChatMemory
from core.datasource.implementations.s3 import S3

read = Read()
write = Write()
metadata = Metadata()
db_connector = DatabaseConnector()
data_profile = DataProfile()

mongo_client = MongoConnector()
mongo_client = mongo_client.client



class MetaProcessor:
    """
    The MetaProcessor class is responsible for executing the complete metadata process. 
    It provides various methods to manage and execute metadata-related operations, 
    including execution of tasks, generation of metadata, and other internal functions 
    necessary for processing such as update, preparing file path, extract, read file, read table,
    generate metadata, generate data profile, upload feather, update history,get step number and  save history
    """
    def __init__(self, session) -> None:
        self.session = session

    @Logger.generate
    def execute(self, source, **kwargs):
        """
        This method executes the complete metadata process by performing several key tasks: 
        extracting a DataFrame based on the source type (file or database), 
        generating metadata for the DataFrame, uploading the DataFrame to a specified Feather path using 
        the provided user information, updating and saving the history, and returning the source ID where
        the data is inserted

        :param source: The source type like file or database.
        :type source: str
        :param kwargs: A dictionary of additional keyword arguments required for the method which includes
                       user_id, chat_id, file_name and file_id
        :type kwargs: dict
        :return:  A boolean indicating success or failure, The source id
        :rtype: bool, str
        """
        try:

            logger.info("Executing metadata and data profile...")
            extract_success, df = self.extract(source, **kwargs)
            metadata_success, metadata_dict = self.generate_metadata(df)
            # data_profile_success, data_profile_dict = self.generate_data_profile(df)
            feather_file_path = os.path.join(BaseConfig.BASE_DIR,BaseConfig.UPLOAD_FOLDER,kwargs["user_id"], ".cache", kwargs["chat_id"], str(uuid.uuid4()) +
                                             ".feather")
            copy_feather_file_path = os.path.join(BaseConfig.BASE_DIR,BaseConfig.UPLOAD_FOLDER,kwargs["user_id"], ".cache", kwargs["chat_id"], str(uuid.uuid4())+ "_copy" +
                                             ".feather")
            kwargs["file_name"]=kwargs["file_name"].replace(".","_")
            feather_path = {"feather_file_path": feather_file_path}
            metadata = {"metadata": metadata_dict}
            # data_profile = {"data_profile": data_profile_dict}
            org_file_id = {"org_file_id": kwargs["file_id"] if source == "file" else None}
            source_db_object_id = { "source_db_object_id": kwargs["file_id"] if source == "file" else kwargs["connection_id"]}
            export_path = {"export_path": None}
            feather_copy = {"feather_copy": copy_feather_file_path}
            export_name = {"export_name": None}
            user_id = {"user_id": kwargs["user_id"]}
            chat_id = {"chat_id": kwargs["chat_id"]}
            file_name = {"file_name": kwargs["file_name"]}
            alias_snatized=CommonUtils().replace_special_chars(kwargs["file_name"])
            file_list_with_alias=CommonUtils().get_chat_files_aliases_document(self.session,kwargs["chat_id"])
            unique_alias=CommonUtils().get_unique_name(alias_snatized,file_list_with_alias)
            dataframe_alias = {"dataframe_alias" : unique_alias}
            kwargs["dataframe_alias"]=unique_alias
            
            type = {"type": kwargs["type"]}
            # To test in local
            # feather_file_path = self.prepare_file_path(feather_file_path)
            status, path = self.upload_feather(feather_file_path, df)
            # self.upload_feather(copy_feather_file_path, df)
            update_info = {}
            # update_info.update(data_profile)
            update_info.update(export_path)
            update_info.update(feather_path)
            update_info.update(file_name)
            update_info.update(type)
            update_info.update(metadata)
            update_info.update(org_file_id)
            update_info.update(source_db_object_id)
            update_info.update(user_id)
            update_info.update(chat_id)
            update_info.update(export_name)
            update_info.update(feather_copy)
            update_info.update(dataframe_alias)
            
            cache = MongoFactory(mongo_client, "cache", session=self.session)
            chats = MongoFactory(mongo_client, "chats", session=self.session)
            insert_success, inserted_feather_id = cache.insert_document(update_info)
            if 'source_id' in kwargs:
                source_id = kwargs['source_id']
            else:
                source_id = str(uuid.uuid4())
            _, modified_count = cache.update_one(inserted_feather_id, "source_id", source_id)
            chat_data={"source_id":source_id,"alias":file_name["file_name"],"type":type["type"]}
            
            append_success, append_modified_count=chats.append_one(kwargs["chat_id"], "files", chat_data)
            update_success, update_modified_count=chats.update_one(kwargs["chat_id"],"cwf",chat_data)
            history_success, history = self.update_history(source, source_id, **kwargs)
            save_success = self.save_history(kwargs["chat_id"], history)
            logger.info("Metadata execute completed!")

            # generates sql create statement
            sql = ChatMemory(self.session).generate_sql_from_dataframe(df, file_name['file_name'])
            # stores the data in memory
            LLMChatBot(user_id["user_id"], chat_id["chat_id"], self.session).store_response("Data", sql)
            
            return True, source_id
        except DatabaseConnectorException as e:
            raise DatabaseConnectorException(e) from e

        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred during Metaprocessor execution Generate: {e}", exc_info=True)
            raise MetadataException("Failed to generate metadata.") from e

    @Logger.generate
    def generate(self, df, **kwargs):
        """
        This method generates metadata for the provided DataFrame and uploads the DataFrame as a Feather file to the specified path. 
        It also utilizes the provided user information for managing the upload process

        :param dataframe: The DataFrame whose metadata has to be generated
        :type dataframe: pandas.DataFrame
        :param kwargs: A dictionary of additional parameters required for the method: user_id, chat_id, file_name and type
        :type kwargs: dict
        :return:  A boolean indicating success or failure, The feather id
        :rtype: bool, str
        """
        try:
           
            logger.info("Generating metadata and data profile..")
            _, metadata_dict = self.generate_metadata(df)
            # data_profile_success, data_profile_dict = self.generate_data_profile(df)
            feather_file_path = os.path.join(BaseConfig.BASE_DIR,BaseConfig.UPLOAD_FOLDER,kwargs["user_id"], ".cache", kwargs["chat_id"], str(uuid.uuid4()) +
                                             ".feather")
            feather_path = {"feather_file_path": feather_file_path}
            kwargs["file_name"] = kwargs["file_name"].replace(".", "_")
            metadata = {"metadata": metadata_dict}
            # data_profile = {"data_profile": data_profile_dict}
            org_file_id = {"org_file_id":  None}
            export_path = {"export_path": None}
            export_name = {"export_name": None}
            user_id = {"user_id": kwargs["user_id"]}
            chat_id = {"chat_id": kwargs["chat_id"]}
            file_name = {"file_name": kwargs["file_name"]}
            alias_snatized=CommonUtils().replace_special_chars(kwargs["file_name"])
            file_list_with_alias=CommonUtils().get_chat_files_aliases_document(self.session,kwargs["chat_id"])
            unique_alias=CommonUtils().get_unique_name(alias_snatized,file_list_with_alias)
            dataframe_alias = {"dataframe_alias" : unique_alias}
            kwargs["dataframe_alias"]=unique_alias
            type = {"type": kwargs["type"]}
            # To test in local
            # feather_file_path = self.prepare_file_path(feather_file_path)
            status, path = self.upload_feather(feather_file_path, df)
            update_info = {}
            # update_info.update(data_profile)
            update_info.update(export_path)
            update_info.update(feather_path)
            update_info.update(file_name)
            update_info.update(type)
            update_info.update(metadata)
            update_info.update(org_file_id)
            update_info.update(user_id)
            update_info.update(chat_id)
            update_info.update(export_name)
            update_info.update(dataframe_alias)
            
            cache = MongoFactory(mongo_client, "cache", session=self.session)
            insert_success, inserted_feather_id = cache.insert_document(update_info)
            source_id = kwargs.get("source_id",str(uuid.uuid4()))
            update_sucess, modified_count = cache.update_one(inserted_feather_id,"source_id",source_id)
            
            chat_data={"source_id":source_id}
            chats = MongoFactory(mongo_client, "chats", session=self.session)
            append_success, modified_count = chats.append_one(kwargs["chat_id"], "files",chat_data)
            update_success, modified_count = chats.update_one(kwargs["chat_id"],"cwf",chat_data)
            logger.info("Returning source id.")
            
            # generates sql create statement
            sql = ChatMemory(self.session).generate_sql_from_dataframe(df, file_name['file_name'])
            logger.info(f"sql {sql}")
            # stores the data in memory
            LLMChatBot(user_id["user_id"], chat_id["chat_id"], self.session).store_response("Data", sql)
            
            return True ,str(source_id)
        except DatabaseConnectorException as e:
            raise DatabaseConnectorException(e) from e

        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred during Metaprocessor execution Generate: {e}", exc_info=True)
            raise MetadataException("Failed to generate metadata.") from e

    @Logger.generate
    def update(self, source_id, dataframe, chat_id, user_id):
        """
        This method updates a Feather file identified by the given feather_id, generates metadata for the updated file, and returns None

        :param dataframe: The DataFrame whose metadata has to be generated
        :type dataframe: pandas.DataFrame
        :param feather_file_id: The feather id
        :type feather_file_id: str
        :return: None
        :rtype: str
        """
        try:
            feather_files = MongoFiles(mongo_client, "cache", session=self.session)
            cache: CacheBase = get_cache(session=self.session)
            feather_files_document = cache.get_item(source_id, user_id, chat_id)

            if feather_files_document is None:
                # cache document does not exist, create document instead
                return

            feather_file_path = feather_files_document["feather_file_path"]
            status, path = self.upload_feather(feather_file_path, dataframe)
            metadata_success, metadata_dict = self.generate_metadata(dataframe)
            
            _, _ = feather_files.update_one_by_fields(source_id, chat_id, user_id, "metadata", metadata_dict)
            logger.info("Metadata update completed!")
            return None
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred during Metaprocessor updation: {e}", exc_info=True)
            raise MetadataException("Failed to update metadata..") from e

    @Logger.generate
    def prepare_file_path(self, file_path):
        """
        This method constructs and returns the full path of a file by combining a given base_path with the specified file_name

        :param file_path: The file path
        :type file_path: str
        :return:  A boolean indicating success or failure, The updated file path
        :rtype: bool, str
        """
        try:
            logger.info("Preparing file path.")
            absolute_path = os.path.abspath(os.path.join(__file__, "../../../.."))
            file_path = os.path.join(absolute_path, "hadoop_local", file_path).replace("\\",'/')
            logger.info("Returning file path..")
            return True, file_path
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while preparing the file path: {str(e)}", exc_info=True)
            raise UtilsException("Failed to prepare file path.") from e

    @Logger.generate
    def extract(self, source, **kwargs):
        """
        This method extracts a DataFrame based on the specified source_type and related details provided in source_details

        :param source: The source type file or database
        :type source: str
        :param kwargs: A dictionary of additional keyword arguments required for the method which includes
                       user_id, chat_id, file_name and file_id
        :type kwargs: dict
        :return:  A boolean indicating success or failure, The dataframe after reading file or database
        :rtype: bool, pandas.dataframe
        """
        try:
            logger.info("Extracting data..")
            if source == "file":
                success, df = self.read_file(**kwargs)
            elif source == "database":
                success, df = self.read_table(**kwargs)
            elif source == "s3":
                success, df = self.read(**kwargs)
            else:
                raise ValueError(f"Invalid value for `source` received. Value should be file or database, received {source}")         
        
            df.columns = [re.sub('[^0-9a-zA-Z]+', '_', col) for col in map(str.lower, df.columns)]
                
            logger.info("Returning extracted dataframe.")
            return True, df
        except DatabaseConnectorException as e:
            raise DatabaseConnectorException(e) from e

        except Exception as e:
            logger.error(f"Operation 'extract' completed with an exception: {str(e)}", exc_info=True)
            raise UtilsException("Failed to extract the data.") from e

    @Logger.generate
    def read_table(self, **kwargs):
        """
        Reads data from a table using the provided keyword arguments connection ID,
        table name, database name, and list of columns 

        :param kwargs: A dictionary of additional keyword arguments required for the method which includes
                       user_id, chat_id, file_name and file_id
        :type kwargs: dict
        :return:  A boolean indicating success or failure, The dataframe after reading table
        :rtype: bool, pandas.dataframe
        """
        try:
            logger.info("Extracting data from table..")
            connection_id = kwargs["connection_id"]
            user_id = kwargs["user_id"]
            connections = MongoFactory(mongo_client, "connections", session=self.session)
            success, connections_document = connections.get_by_id(connection_id)
            catalog=kwargs.get("table_name")
            if catalog:
                database_name=connections_document.get("type")#just as we have table_name in data and catalog need to fix this later
                pass
            else:
                catalog = kwargs["catalog"]
                database_name = kwargs["database_name"]
            columns = kwargs["columns"]
            db = db_connector.create_object(database_name)
            users = MongoFiles(mongo_client, "users", session=self.session)
            get_success, user_document = users.get_by_id(user_id)
            settings = user_document.get('settings')
            num_rows = 100
            if 'files' in settings and 'num_records' in settings['files']:
                if settings['files']['num_records'] > 0:
                    num_rows = settings['files']['num_records']
            else:
                raise ValueError("Check user settings format in DB, files and num_records key are required")
            logger.info(f"Fetch record num_rows set to {num_rows}")
            connection = db.connect(connections_document["connection_details"],engine=database_name)
            df = db.fetch_data(
                connections_document["connection_details"],
                catalog, columns,
                engine=database_name,
                connection=connection,
                num_rows=num_rows)
            logger.info("Returning extracted dataframe.")
            return True, df
        except DatabaseConnectorException as e:
            raise DatabaseConnectorException(e) from e

        except Exception as e:
            logger.error(f"Operation 'read_table' completed with an exception: {str(e)}", exc_info=True)
            raise UtilsException(f"Failed to extract the data from table.") from e

    @Logger.generate
    def read(self, **kwargs):
        """
        This method reads a s3 file based on the parameters provided in the kwargs dictionary, which includes the user_id and file_id

        :param kwargs: A dictionary of additional keyword arguments required for the method which includes
                       user_id, chat_id, file_name and file_id
        :type kwargs: dict
        :return:  A boolean indicating success or failure, The dataframe after reading table
        :rtype: bool, pandas.dataframe
        """
        try:

            logger.info("Extracting data from file..")
            user_id = kwargs["user_id"]
            connection_id = kwargs["connection_id"]
            catalog = kwargs.get("file_name")
            users = MongoFiles(mongo_client, "users", session=self.session)
            get_success, user_document = users.get_by_id(user_id)
            if not user_document:
                settings = None
            else:
                settings = user_document.get('settings', None)
            num_rows = settings.get('files', {}).get('num_records', None) if settings else None
            connections = MongoFiles(mongo_client, "connections", session=self.session)
            success, connection_details = connections.get_by_id(connection_id)
            if not success or connection_details is None:
                raise ValueError(f"Invalid connection_id: {connection_id}")
            try:
                db = db_connector.create_object("s3")
                connection = db.connect(connection_details["connection_details"],engine="s3")
                columns = kwargs.get("columns", [])
                df = db.fetch_data(connection_details["connection_details"],
                    catalog, columns,
                    engine="s3",
                    connection=connection,
                    num_rows=num_rows)
                success = True
            except Exception as fetch_err:
                logger.error(f"Failed to fetch data for {catalog}", exc_info=True)
                success = False
            logger.info("Returning extracted dataframe.")
            return success, df
        except Exception as e: # pragma: no cover
            logger.error(f"Operation 'read' Completed with Exception: {str(e)}", exc_info=True)
            raise UtilsException("Failed to extract data from file.") from e

    @Logger.generate
    def read_file(self, **kwargs):
        """
        This method reads a table based on the parameters provided in the kwargs dictionary, which includes the user_id and file_id

        :param kwargs: A dictionary of additional keyword arguments required for the method which includes
                       user_id, chat_id, file_name and file_id
        :type kwargs: dict
        :return:  A boolean indicating success or failure, The dataframe after reading table
        :rtype: bool, pandas.dataframe
        """
        try:
            logger.info("Extracting data from file..")
            user_id = kwargs["user_id"]
            file_id = kwargs["file_id"]
            files = MongoFiles(mongo_client, "files", session=self.session)
            file_success, files_document = files.get_by_file_id(user_id, file_id)
            file_name = files_document["file_name"]
            file_type = files_document["file_type"]
            file_path = files_document["file_path"]
            catalog = kwargs.get("catalog", {})
            users = MongoFiles(mongo_client, "users", session=self.session)
            get_success, user_document = users.get_by_id(user_id)
            if not user_document:
                settings = None
            else:
                settings = user_document.get('settings', None)
            # To test in local
            # file_path = self.prepare_file_path(file_path)
            
            function = getattr(read, file_type.split(".")[-1])
            success, df = function(file_path, settings, catalog)
            logger.info("Returning extracted dataframe.")
            return success, df
        except Exception as e: # pragma: no cover
            logger.error(f"Operation 'read_file' Completed with Exception: {str(e)}", exc_info=True)
            raise UtilsException("Failed to extract data from file.") from e

    @staticmethod
    @Logger.generate
    def generate_metadata(dataframe):
        """
        This method generates metadata for the provided DataFrame and returns a dictionary containing details about the dataset. 
        The metadata includes summary statistics and other relevant information

        :param dataframe: Dataframe from which metadata has to be inferred
        :type dataframe: pandas.dataframe
        :return:  A boolean indicating success or failure, Dictionary of metadata
        :rtype: bool, dict
        """
        try:
            logger.info("Generating metadata.")
            success, metadata_dict = metadata.execute(dataframe)
            logger.info("Returning metadata dict.")
            return True, metadata_dict
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating metadata: {str(e)}", exc_info=True)
            raise MetadataException("Failed to generate metadata.") from e

    @staticmethod
    @Logger.generate
    def generate_data_profile(dataframe):
        """
        This method generates a data profile for the provided DataFrame and returns the dictonary of 
        data profile which includes summary statistics and other relevant information about the dataset 

        :param dataframe: Dataframe from which metadata has to be inferred
        :type dataframe: pandas.dataframe
        :return:  A boolean indicating success or failure, Dictionary of data profile
        :rtype: bool, dict
        """
        try:
            logger.info("Generating data profile.")
            success, data_profile_dict = data_profile.execute(dataframe)
            logger.info("Returning data profile dict.")
            return True, data_profile_dict
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating data profile: {str(e)}", exc_info=True)
            raise MetadataException("Failed to generate data profile.") from e


    @staticmethod
    @Logger.generate
    def upload_feather(path, dataframe):
        """
        This method writes the given DataFrame to a Feather file at the specified path and returns path and status

        :param path: Path of the sample file
        :param dataframe: The dataframe which has to be written/ saved
        :type dataframe: pandas.dataframe
        :return:  A boolean indicating success or failure, The path where the file is saved
        :rtype: bool, str
        """
        try:
            logger.info("Uploading feather.")
            directory = os.path.dirname(path)
            # Create the directory if it doesn't exist
            if not os.path.exists(directory):
                os.makedirs(directory)
            status, path = write.feather(dataframe, path)
            logger.info("Successfully uploaded feather.")
            return status, path
        except Exception as e: # pragma: no cover
            logger.error(f"Operation 'upload_feather' Completed with Exception: {str(e)}", exc_info=True)
            raise UtilsException("Failed to upload the feather file.") from e

    @Logger.generate
    def update_history(self, source, source_id_cache, **kwargs):
        """
        This method updates the operation history with details of a specific step. 
        It records the provided step details, including function or operation performed, 
        and results, to maintain an accurate and comprehensive history of operations

        :param source: The source type file or database
        :type source: str
        :param source_id_cache: The source id of the cache
        :type source_id_cache: str
        :param kwargs: A dictionary of additional keyword arguments required for the method which includes
                       user_id, chat_id, file_name and file_id
        :type kwargs: dict
        :return:  A boolean indicating success or failure, The updated history
        :rtype: bool, dict
        """
        try:
            logger.info("Updating history..")
            if source == "file":
                function = "read_files"
                parameters = {
                        "file_id": kwargs["file_id"],
                        "file_name": kwargs["file_name"], # feather id in case of files
                    }
            elif source == "database":
                function = "read_tables"
                parameters = {
                        "table_name": kwargs["catalog"],
                        "connection_id": kwargs["connection_id"],
                        "columns": kwargs["columns"],
                    }
            elif source == "s3":
                function = "read"
                parameters = {
                        "file_name": kwargs["catalog"],
                        "connection_id": kwargs["connection_id"],
                        "type": kwargs["type"],
                        "source_type": source
                    }
            # status,step=self.get_step_number(kwargs["chat_id"])
            history = {
                "id": str(uuid.uuid4()),
                # "step": step,
                "status": "PASS",
                "function": function,
                "parameters": parameters,
                "output": {
                    "dataframe_alias": kwargs["dataframe_alias"],
                    "source_id" : source_id_cache
                }
            }
            logger.info("Successfully updated history..")
            return True, history
        except Exception as e:
            logger.error(f"Operation 'update_history' completed with an exception: {str(e)}", exc_info=True)
            raise UtilsException("Failed to update the history.") from e

    @Logger.generate
    def get_step_number(self, chat_id: str) -> int:
        """
        This method retrieves the next available step number in a sequence. 
        It is typically used to determine the appropriate number for the upcoming step in a series of 
        operations or processes, ensuring that each step is assigned a unique and sequential number

        :param chat_id: The unique id for the chat
        :type chat_id: str
        :return: A boolean indicating success or failure, The next step number
        :rtype: bool, int
        """
        try:
            logger.info("Getting the step number.")
            step_number = 0
            chats = MongoFactory(mongo_client, "chats", session=self.session)
            get_success, chat_document = chats.get_by_id(chat_id)

            if not get_success:
                # Create the "history" array if it doesn't exist
                update_success, modified_count= chats.update_one(chat_id, "history", [])
            get_success, chat_document = chats.get_by_id(chat_id)
            history = chat_document.get("history", [])
            logger.info(f"History: {history}")
            if history:
                # Find the last step number from the "history" array
                filtered_history = [item for item in history if item["step"] not in [ "export","export_table","step_export"]]
                step_numbers = [int(item["step"]) for item in filtered_history]
                if step_numbers:
                    step_number = max(step_numbers) + 1
            logger.info("Returning the step number.")
            return True, step_number
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while getting step number:{str(e)}", exc_info=True)
            raise UtilsException("Failed to get the step number.") from e

    @Logger.generate
    def save_history(self, chat_id: str, history: dict) -> None:
        """
        This method saves the operation history along with user information to a specified storage medium. 
        It records details about the user and the operation history to ensure that all relevant data is preserved

        :param chat_id: The unique id for the chat
        :type chat_id: str
        :param history: A dictionary containing the history entries to be saved
        :type history: dict
        :return: A boolean indicating success or failure
        :rtype: bool
        """
        try:
            logger.info("Saving the history.")
            chats = MongoFactory(mongo_client, "chats", session=self.session)
            get_success, chat_document = chats.get_by_id(chat_id)
            append_success, modified_count = chats.append_one(chat_id, "history", history)
            logger.info("Saved the history.")
            return True
        except Exception as e: # pragma: no cover
            logger.error(f'An error occurred while saving history: {str(e)}', exc_info=True)
            raise UtilsException("Failed to save the history.") from e
    
    def delete_files(self, chat_id, source_id, should_save_history: bool = True):
        try:
            logger.info(f"(debug) delete_files called for chat_id {chat_id} source_id {source_id}")
            chat = Chat(session=self.session)
            cache = Cache(session=self.session)
            success, chat_doc = chat.get(chat_id)
            loaded_files = chat_doc.get("files")
            logger.info(f"(debug) files currently loaded {loaded_files}")
            cwf = chat_doc.get("cwf")
            new_files = [file for file in loaded_files if file.get("source_id")!=source_id]
            logger.info(f"(debug) new files to be updated {new_files}")
            if cwf.get("source_id") == source_id:
                chat.update(chat_id, "cwf", {})
            chat.update(chat_id, "files", new_files)
            history = {
                    "id": str(uuid.uuid4()),
                    "status": "PASS",
                    "function": "delete_files",
                    "parameters": {
                        "source_id":source_id
                    },
                    "output": None
                }
            if should_save_history:
                self.save_history(chat_id, history)
            try:
                success, cache_doc = cache.filter({
                    "source_id":source_id,
                    "chat_id": chat_id,
                    "user_id": chat_doc.get("user_id")
                })
                if success:
                    feather_file_path = cache_doc[0].get("feather_file_path")
                    cache.delete_one_by_query(
                        {"source_id": source_id, "chat_id": chat_id, "user_id": chat_doc.get("user_id")})
                    os.remove(feather_file_path)
                logger.info(f"(debug) delete files step complete")
            except Exception as e:
                logger.error(f'An error occurred while deleting cache from mongo: {str(e)}', exc_info=True)
            return True
        except Exception as e:
            logger.error(f'An error occurred while deleting file: {str(e)}', exc_info=True)
            raise UtilsException("Failed to delete the file.") from e
        