from typing import Any, Dict, List, Optional, Tuple, Union
import yaml
import json
import pandas as pd
from .utils import DFInformation, CreateDFDictionary , ReRunUtilities

from ....models.connector import MongoConnector
from ....etl.extract.file_operations.read import Read
from ....etl.metadata.file_operations.write import Write
from ....exceptions.exception import *
from ....logger.logger import Logger, logger
from ...data.chat import Chat
from ...data.file import File
from ...data.cache import Cache
from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase
from ....etl.metadata.meta_processor import MetaProcessor
from ....models.mongo.mongo_files import MongoFiles
from ....models.mongo.mongo_factory import MongoFactory

read = Read()
write = Write()
mongo = MongoConnector()

mongo_client = mongo.client

class ReRunService:# pragma: no cover
    """Service for re-running a data processing pipeline.

    Manages the execution and re-running of data processing pipelines by
    interacting with various MongoDB collections and processing operations.

    Attributes:
        session (Session): The database session used for operations.
        chats_collection (MongoFactory): MongoDB factory for chat documents.
        cache_collection (MongoFactory): MongoDB factory for cache documents.
        files_collection (MongoFiles): MongoDB factory for file documents.
        processor (Processor): Processor for executing operations.
        metaprocessor (MetaProcessor): MetaProcessor for additional data handling.
        create_df_dict (CreateDFDictionary): Utility for creating data frame dictionaries.
        rerun_utilities (ReRunUtilities): Utilities for re-running pipelines.
        _dataframe_info (DFInformation): Utility for retrieving data frame information, also tracks global state
    """
    def __init__(self, session):
        """Initializes the ReRunService with a session and sets up required components.

        Args:
            session (Session): The database session to use for operations.
        """
        from ....etl.transfrom.process.processor import Processor
        self.session = session
        self.processor = Processor(self.session)
        self.metaprocessor = MetaProcessor(self.session)
        self.create_df_dict = CreateDFDictionary(self.session)
        self.rerun_utilities=ReRunUtilities()
        self.files_collection = MongoFiles(mongo_client, "files", session=self.session)
        self.chat_collection = MongoFactory(mongo_client, "chats", session=self.session)
        self._dataframe_info = DFInformation({})
        self.destination_id = None
        self.destination_alias = None

    def _get_pipeline_from_chat_history(self, chat_id: str) -> List:
        _, chat = Chat(self.session).get(chat_id)
        return chat.get("history",[])

    @Logger.generate
    def dry_run(self, chat_id: str, pipeline: Optional[str] = None) -> Tuple[bool, str, List]:
        """Re-runs the data processing pipeline for a given chat ID.

        Args:
            chat_id (str): The ID of the chat document to use.
            pipeline (list, optional): The pipeline to run. If None, it fetches the pipeline from chat history.

        Returns:
            tuple: A tuple containing a boolean indicating success and a message.

        Raises:
            ValueError: If there are discrepancies in dataframe alias and source ID lengths.
        """
        if pipeline is None:
            pipeline = self._get_pipeline_from_chat_history(chat_id)
        else:
            json_string = json.dumps(yaml.safe_load(pipeline), indent=4)
            pipeline = json.loads(json_string)
        
        execution_status, _ = self.run_pipeline(pipeline, chat_id)
        if not execution_status:
            return False, "Failed to Run pipeline", []
        # data = self.get_preview_data(self.destination_id, self.destination_alias)
        return True, "Successfully Ran Pipeline"
        
    def pipeline(self, chat_id: str, pipeline: Optional[list] = None, update_job_mode: bool = True) -> Tuple[bool, str]:
        """
        Executes a pipeline for a given chat session.

        Args:
            chat_id (str): The ID of the chat session.
            pipeline (list, optional): The pipeline to execute. If None, retrieves the pipeline from the chat history.

        Returns:
            tuple: A tuple containing:
                - bool: Success status of the pipeline execution.
                - str: Message indicating success or failure.
        """
        if pipeline is None:
            _, chat = Chat(self.session).get(chat_id)
            pipeline = chat.get("history",[])
            if not pipeline:
                pipeline=[]
        success, updated_pipeline = self.run_pipeline(pipeline, chat_id)
        if success:
            try:
                self.save_data(chat_id, updated_pipeline)
                if update_job_mode:
                    Chat(self.session).update_mode(chat_id, "yaml")
                return True, "Successfully Ran Pipeline", updated_pipeline
            except Exception as e:
                logger.error(f"Error when saving pipeline data - {str(e)}", exc_info=True)
                raise RuntimeError(str(e)) from e
        else:
            return False, "Failed to run Pipeline", []

    def _set_destination_id_and_alias(self, pipeline_item) -> None:
        if "output" not in pipeline_item:
            return
        
        output = pipeline_item.get("output")
        # In case of Pytool, output is List[Dict] as there are multiple output and in all other cases, it is Dict

        if isinstance(output, list):
            output = output[-1]

        # TODO: Check if there is any case where output block may not have these keys
        self.destination_alias = output.get("dataframe_alias")
        self.destination_id = output.get("source_id")

        return

    def _handle_read_files_intent(self, pipeline_item, user_id):
        parameters = pipeline_item.get("parameters", {})
        file_id = parameters.get("file_id")
        
        params = {
            "user_id": user_id,
            "file_id": file_id
        }
        _, df = self.metaprocessor.read_file(**params)

        return df

    def _handle_read_tables_intent(self, pipeline_item, chat_id, user_id):
        parameters = pipeline_item.get("parameters", {})
        parameters["user_id"] = user_id

        _, df = self.metaprocessor.read_table(**parameters)
        return df

    def _handle_read_intent(self, pipeline_item, chat_id, user_id):
        parameters = pipeline_item.get("parameters", {})
        parameters["user_id"] = user_id

        _, df = self.metaprocessor.read(**parameters)
        return df
    
    def _get_user_id_for_chat(self, chat_id):
        return self.chat_collection.get_by_id(chat_id)[1]["user_id"]

    @Logger.generate
    def run_pipeline(self, pipeline: List[Dict[str, Any]], chat_id: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Processes and executes a series of pipeline operations.

        Args:
            pipeline (list): A list of dictionaries representing pipeline operations.

        Returns:
            tuple: A tuple containing:
                - bool: Success status of the pipeline execution.
                - list: Updated pipeline after execution.
        """
        try:
            user_id = self._get_user_id_for_chat(chat_id)
            for item in pipeline:
                intent = item.get("function")
                operation_class = self.processor.operation_mapping.get(intent)
                parameters = item.get("parameters", {})
                isoutput = item.get("output", False)
                if isoutput == 'null':
                    isoutput = False

                if isoutput:
                    # if output is present we set destination alias and id
                    self._set_destination_id_and_alias(item)
                else:
                    self.destination_id = None
                    self.destination_alias = None

                if intent in ["read_tables", "read_files", "read", "delete_files"]:
                    # For read intents, we load data from the sources
                    #   in dataframe and update the config dict with
                    #   this dataframe
                    _df = None
                    if intent == 'read_files':
                        _df = self._handle_read_files_intent(item, user_id)
                        
                    if intent == 'read_tables':
                        _df = self._handle_read_tables_intent(item, chat_id, user_id)

                    if intent == 'read':
                        _df = self._handle_read_intent(item, chat_id, user_id)

                    if intent == 'delete_files':
                        source_id = parameters.get("source_id")
                        self._dataframe_info.config_dict.pop(source_id, None)
                        self.metaprocessor.delete_files(chat_id, source_id, should_save_history=False)
                    
                    if isoutput:
                        # TODO: need to refactor following function
                        self._dataframe_info.config_dict = self.rerun_utilities.update_configurations(
                            self._dataframe_info.config_dict,
                            self.destination_alias,
                            self.destination_id,
                            _df,
                            intent
                        )
                        if not self.destination_id:
                            self.destination_id = self._dataframe_info.get_id_by_alias(self.destination_alias)
                        item['output']['source_id'] = self.destination_id
                        item['output']['dataframe_alias'] = self.destination_alias

                elif intent in ["joins", "union"]:
                    
                    dataframe_aliases = parameters.get("dataframe_aliases")
                    source_ids = parameters.get("source_id")

                    df_list=[]
                    if dataframe_aliases and source_ids:
                        if len(dataframe_aliases) != len(source_ids):
                            raise ValueError("Extra parameters found in alias or id. Both lists must be of the same length.")
                        for alias, id in zip(dataframe_aliases, source_ids):
                            df = self._dataframe_info.get(id=id,alias=alias)
                            df_list.append(df)
                    elif dataframe_aliases:
                        parameters['source_id']=[] #remove It later this is just to make yml same as old
                        for alias in dataframe_aliases:
                            df = self._dataframe_info.get(alias=alias)
                            parameters['source_id'].append(self._dataframe_info.get_id_by_alias(alias))#remove It later this is just to make yml same as old
                            df_list.append(df)
                    elif source_ids:
                        for id in source_ids:
                            df = self._dataframe_info.get(id=id)
                            df_list.append(df)
                    else:
                        raise ValueError("Either dataframe_aliases or source_ids must be provided.")
                    df, status, metadata_status, msg, new_df, details = operation_class().execute(df_list, parameters)
                    if not status:
                        raise RuntimeError(f"Pipeline step {intent} failed - {msg}")
                    
                    if isoutput:
                        self._dataframe_info.config_dict = (
                        self.rerun_utilities.update_configurations(
                            self._dataframe_info.config_dict, 
                            alias=self.destination_alias, 
                            source_id=self.destination_id,
                            df=df,
                            intent_name=intent
                            )
                        )
                        if len(isoutput)>0:
                            dest_id=self._dataframe_info.get_id_by_alias(self.destination_alias)
                            item['output']['source_id']=dest_id
                            item['output']['dataframe_alias']=self.destination_alias

                elif intent == "pytool":
                    _, chat_doc = Chat(self.session).get(chat_id)
                    user_id = chat_doc.get("user_id")
                    try:
                        _, _, output, self._dataframe_info.config_dict = operation_class().execute(self._dataframe_info.config_dict, parameters, {"user_id":user_id, "chat_id":chat_id}, self.session)
                    except Exception as e:
                        raise RuntimeError(f"Pipeline step {intent} failed - {e}")
                    item['output'] = output
                elif intent == "export":
                    continue
                else:
                    name = parameters.get("dataframe_alias")
                    source_id = parameters.get("source_id")
                    df = self._dataframe_info.get(id=source_id, alias=name)
                    df, status, _, msg, _, _ = operation_class().execute(df, parameters)
                    if not status:
                        raise RuntimeError(f"Pipeline step {intent} failed - {msg}")
                    if self.destination_alias or self.destination_id:
                        pass
                    else:
                        self.destination_alias = name
                        self.destination_id = source_id
                    self._dataframe_info.config_dict = self.rerun_utilities.update_configurations(
                        self._dataframe_info.config_dict,
                        alias=self.destination_alias,
                        source_id=self.destination_id,
                        df=df,
                        intent_name=intent
                    )
                    if isoutput:
                        if not self.destination_id:
                            self.destination_id = self._dataframe_info.get_id_by_alias(self.destination_alias)
                        item['output']['source_id'] = self.destination_id
                        item['output']['dataframe_alias'] = self.destination_alias
            return True, pipeline
        except Exception as e:
            logger.error(f"Failed to run pipeline - {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to run pipeline: {str(e)}") from e
    
    def save_data(self, chat_id: str, pipeline: List[Dict[str, Any]]) -> None:
        """
        Saves the updated pipeline to the database and resets relevant configurations.

        data = []
        data = self.get_preview_data(destination_id, destination_alias)
        return True, "Successfully Ran Pipeline", data

        Returns:
            None
        """
        chat = Chat(self.session)
        success, updated_pipeline = self.final_update(chat_id, self._dataframe_info.config_dict, pipeline)
        if updated_pipeline == []:
            chat.update(chat_id, "cwf", {})
        chat.update(chat_id, "history", updated_pipeline)
        chat.update(chat_id, "is_undoRedoAvailable", False)
    
    #TODO:- We need to load data in the chat files and cwf if it not present
    def get_preview_data(self, dataframe_id, dataframe_alias):
        """Returns preview data"""
        df = self._dataframe_info.config_dict.get(dataframe_id).get("df")
        _, preview_info = self.processor.preview(dataframe_id, dataframe_alias, df)
        return preview_info

    def generateData(self, dataframe_alias: str, df: Any, chat_id: str) -> str:
        """Generates a new data entry and updates the chat document.

        Args:
            dataframe_alias (str): The alias for the data frame.
            df (DataFrame): The data frame to generate.
            chat_id (str): The ID of the chat document.

        Returns:
            str: The ID of the newly inserted data.
        """
        _, chat = Chat(self.session).get(chat_id)
        user_id = chat.get("user_id")
        user_info = {}
        user_info["file_name"] = dataframe_alias
        user_info["type"] = "csv"
        user_info["user_id"] = user_id
        user_info["chat_id"] = chat_id
        if df is None:
            df = pd.DataFrame()
        _ , source_id =  self.metaprocessor.generate(df,**user_info)
        
        return source_id

    def updateData(self, dataframe: Any, source_id: str, chat_id: str, user_id: str) -> None:
        """Updates an existing data entry with a new data frame.

        Args:
            dataframe (DataFrame): The updated data frame.
            source_id (str): The ID of the data entry to update.
        """
        self.metaprocessor.update(source_id, dataframe, chat_id, user_id)

    def updateExistingAlias(self, alias: str, id: str) -> None:
        """Updates the data frame alias in the cache collection.

        Args:
            alias (str): The new alias for the data frame.
            id (str): The ID of the data frame.
        """
        Cache(self.session).update_one_by_source_id_value(id, "dataframe_alias",alias)

    def final_update(self, chat_id: str, _: Dict[str, Any], pipeline: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]]]: 
        """Finalizes the update process by handling data frame replacements and cache updates.

        Args:
            chat_id (str): The ID of the chat document.
            _ (dict): The global dictionary containing data frame configurations (Not needed anymore)
            pipeline (list): The updated pipeline.

        Returns:
            tuple: A tuple containing a boolean indicating success and the updated pipeline.
        """ 
        success, chat = Chat(self.session).get(chat_id)
        files = chat.get("files", [])
        user_id = chat.get("user_id", "")
        history = pipeline
        ids = list(self._dataframe_info.config_dict.keys())
        files_ids = [file.get("source_id") for file in files]
        for id in ids:
            cache: CacheBase = get_cache(session=self.session)
            cache_doc_present = cache.get_item(id, user_id, chat_id)
            
            if id in files_ids and cache_doc_present is not None:
                dataframe = self._dataframe_info.config_dict[id]["df"]
                alias= self._dataframe_info.config_dict[id]['alias']
                self.updateData(dataframe, id, chat_id=chat_id, user_id=chat["user_id"])
                self.updateExistingAlias(alias,id)
            else:
                dataframe = self._dataframe_info.config_dict[id]["df"]
                dataframe_alias = self._dataframe_info.config_dict[id]["alias"]
                inserted_feather_id=self.generateData(dataframe_alias, dataframe, chat_id)
                self._dataframe_info.config_dict[inserted_feather_id] = self._dataframe_info.config_dict.pop(id)
                self.replace_source_id(history,id,inserted_feather_id)
        
        set_files = set(files_ids)
        set_global = set(self._dataframe_info.config_dict.keys())
        
        not_in_global = [item for item in set_files if item not in set_global]
        common_elements = [{"source_id": value, "alias": self._dataframe_info.config_dict[value].get("alias", "")} for value in set_global]
        for id in not_in_global:
            Cache(self.session).delete_one_by_query({"source_id": id, "chat_id": chat_id, "user_id": user_id})
        Chat(self.session).update(chat_id,"files",common_elements)
        
        return True, history

    def replace_source_id(self, json_obj: Dict[str, Any], old_id: str, new_id: str) -> None:
        """Recursively replaces old source IDs with new source IDs in the pipeline.

        Args:
            json_obj (dict or list): The JSON object or list to process.
            old_id (str): The old source ID to replace.
            new_id (str): The new source ID to use.
        """
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                if key == 'source_id' and value == old_id:
                    json_obj[key] = new_id
                else:
                    self.replace_source_id(value, old_id, new_id)
        elif isinstance(json_obj, list):
            for item in json_obj:
                self.replace_source_id(item, old_id, new_id)
    
    def run_and_return_last_df(self, source_id: str, chat_id: str, pipeline: Optional[str] = None, ):
        execution_status, _ = self.run_pipeline(pipeline, chat_id)
        if not execution_status:
            return False, None
        return source_id, self._dataframe_info.config_dict.get(source_id)
        