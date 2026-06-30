
import json
from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase
from ...data.chat import Chat, JobModes
from ....models.mongo.mongo_factory import MongoFactory
from ....configurations.api.config import BaseConfig
from ....logger.logger import Logger, logger
from ....models.connector import MongoConnector
from ....etl.metadata.meta_processor import MetaProcessor
from ..rerun.service import ReRunService
from ....utilities.utilities import CommonUtils
from ..airflow_service.service import AirflowAPI
from .utils import ChatUtils
from src.api.services.base.service_parent import ServiceParent
import os
import shutil
import yaml

from typing import List

class ChatService(ServiceParent):
    """
    Service class for managing chat-related operations in a chat system.

    :param session: The database session for interacting with MongoDB.
    :type session: object, optional
    """

    def __init__(self,session=None):
        """
        Constructor method.

        :param session: The database session for interacting with MongoDB.
        :type session: object, optional
        """
        super().__init__(session)
        self.mongo_chats = MongoFactory(self.client, "chats", session=self.session)
        self.mongo_cache = MongoFactory(self.client, "cache", session=self.session)
        self.mongo_schedule = MongoFactory(self.client, "schedule", session=self.session)
        self.mongo_files = MongoFactory(self.client, "files", session=self.session)
        self.mongo_langchain = MongoFactory(self.client, "langchain", session=self.session)
        self.cache: CacheBase = get_cache(session=self.session)



    @Logger.generate
    def create_chat(self, user_id, chat_name, service_mode: str = "DTS"):
        """
        Creates a new chat for the given user.

        :param user_id: The ID of the user creating the chat.
        :type user_id: str
        :param chat_name: The name of the chat to be created.
        :type chat_name: str
        :param service_mode: The mode of the service (DTS or DMS)
        :type service_mode: str
        :return: A dictionary with success status, chat details, and HTTP status code.
        :rtype: tuple(dict, int)
        :raises Exception: If there is an error in creating the chat.
        """
        try:
            if not chat_name:
                raise Exception(f"Session ID and chat name are required: user_id: {user_id} and chat_name: {chat_name}")
                # return {"success": False, "msg": "Session ID and chat name are required."}, 400

            data = {
                "user_id": user_id,
                'chat_name': chat_name,
                "job_mode": JobModes.LLM.value, #default mode when creating a chat
                "service_mode": service_mode
            }
            status, inserted_id = self.mongo_chats.insert_document(data)
            _, _ = self.mongo_langchain.insert_document({
                "user_id": user_id,
                "chat_id": str(inserted_id),
                "messages": []
            })
            user_folder = os.path.join(BaseConfig.BASE_DIR, BaseConfig.UPLOAD_FOLDER, str(user_id), ".cache", str(inserted_id))
            os.makedirs(user_folder, exist_ok=True)
            logger.info("Successfully created new chat")
            return {
                "success": True,
                "chat_id": str(inserted_id),
                "chat_name": chat_name
            }, 200
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            self.session.abort_transaction()
            return {"success": False, "msg": f"{e}"}, 400

    @Logger.generate
    def update_chat(self, user_id, chat_id, chat_name):
        """
        Updates the name of an existing chat.

        :param user_id: The ID of the user updating the chat.
        :type user_id: str
        :param chat_id: The ID of the chat to be updated.
        :type chat_id: str
        :param chat_name: The new name for the chat.
        :type chat_name: str
        :return: A dictionary with success status, updated chat details, and HTTP status code.
        :rtype: tuple(dict, int)
        :raises Exception: If there is an error in updating the chat.
        """
        try:
            if not chat_name:
                raise Exception(f"Chat name is required with user_id: {user_id} and chat_id: {chat_id}")
                # return {"success": False, "msg": "Chat name is required."}, 400
            
            status, result = self.mongo_chats.update_one(chat_id, "chat_name", chat_name)
            if bool(result):
                logger.info("Successfully updated chat")
                return {
                    "success": True,
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "chat_name": chat_name
                }, 200
            else:
                raise Exception(f"Chat not found with user_id: {user_id}, chat_id: {chat_id} and chat_name: {chat_name}")
                # return {
                #     "success": False,
                #     "msg": "Chat not found."
                # }, 404
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            # self.session.abort_transaction()
            self._safe_abort_transaction()
            return {
                    "success": False,
                    "msg": f"{e}"
                }, 400
            
    @Logger.generate
    def update_dms_progress(self, user_id, chat_id, payload):
        """
        Updates the progress/configuration details of a DMS chat.

        :param user_id: The ID of the user updating the chat.
        :type user_id: str
        :param chat_id: The ID of the chat.
        :type chat_id: str
        :param payload: The payload containing dms_migration_mode, source_details, and destination_details.
        :type payload: dict
        :return: A dictionary with success status and a message.
        """
        try:
            if not chat_id:
                raise Exception("chat_id is required.")
                
            status, chat = self.mongo_chats.get_by_id(chat_id)
            if not chat:
                raise Exception(f"Chat not found with chat_id: {chat_id}")
            
            if chat.get("service_mode") != "DMS":
                raise Exception(f"Invalid service_mode. Expected DMS, got {chat.get('service_mode')}")
            
            for key in ["dms_migration_mode", "source_details", "destination_details"]:
                if key in payload:
                    self.mongo_chats.update_one(chat_id, key, payload[key])
            
            logger.info("Successfully updated DMS progress for chat")
            return {
                "success": True,
                "msg": "chat successfully updated"
            }, 200
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            self._safe_abort_transaction()
            return {"success": False, "msg": f"{e}"}, 400

    @Logger.generate
    def get_dms_progress(self, user_id, chat_id):
        """
        Retrieves the progress/configuration details of a DMS chat.

        :param user_id: The ID of the user fetching the chat details.
        :type user_id: str
        :param chat_id: The ID of the chat.
        :type chat_id: str
        :return: A dictionary with success status, data payload, and a message.
        """
        try:
            if not chat_id:
                raise Exception("chat_id is required.")
                
            status, chat = self.mongo_chats.get_by_id(chat_id)
            if not chat:
                raise Exception(f"Chat not found with chat_id: {chat_id}")
            
            if chat.get("service_mode") != "DMS":
                raise Exception(f"Invalid service_mode. Expected DMS, got {chat.get('service_mode')}")
            
            data = {"chat_id": chat_id}
            for key in ["dms_migration_mode", "source_details", "destination_details", "service_mode"]:
                if key in chat:
                    data[key] = chat[key]
            
            logger.info("Successfully fetched DMS progress for chat")
            return {
                "success": True,
                "data": data,
                "msg": "DMS progress fetched successfully"
            }, 200
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            return {"success": False, "msg": f"{e}"}, 400

            

    @Logger.generate
    def delete_chat(self, user_id, chat_id):
        """
        Deletes an existing chat and its associated files.

        :param user_id: The ID of the user deleting the chat.
        :type user_id: str
        :param chat_id: The ID of the chat to be deleted.
        :type chat_id: str
        :return: A dictionary with success status, deletion message, and HTTP status code.
        :rtype: tuple(dict, int)
        :raises Exception: If there is an error in deleting the chat.
        """
        try:
            status, chat_details = self.mongo_chats.get_by_id(chat_id)
            if not chat_details:
                raise Exception(f"Failed to delete chat with user_id: {user_id} and chat_id: {chat_id}")
                # return {"success": False, "msg": "Failed to delete chat."}, 500
            status,delete_result = self.mongo_chats.delete_all(chat_id)
            logger.info("deleted chat from mongo")
            if not delete_result:
                raise Exception(f"Failed to delete chat from database with user_id: {user_id} and chat_id: {chat_id}")
                # return {"success": False, "msg": "Failed to delete chat from database."}, 500

            self.mongo_cache.delete_all_by_key_value("chat_id", chat_id)
            
            success_msg, schedules = self.mongo_schedule.get_all_by_id_key_value("chat_id", chat_id)
            schedule_ids = [str(schedule.get("_id")) for schedule in schedules if schedule.get("_id")]
            if schedule_ids:
                response = AirflowAPI(session=self.session).delete_schedule({"schedule_ids": schedule_ids})
                logger.info(f"Deleted schedules: {response}")
            else:
                logger.info("No schedules found to delete.")
            
            self.mongo_schedule.delete_all_by_key_value("chat_id", chat_id)
            user_folder = os.path.join(BaseConfig.BASE_DIR, BaseConfig.UPLOAD_FOLDER, str(user_id), ".cache", chat_id)
            try:
                shutil.rmtree(user_folder, ignore_errors=True)
                logger.info("Successfully deleted chat")
            except OSError as e:
                logger.error(f"Error deleting directory: {e}", exc_info=True)
                # return {"success": False, "msg": "Failed to delete chat."}, 500
            return {"success": True, "msg": "Chat deleted successfully.", "chat_id": chat_id}, 200
        except Exception as e:
            logger.error(f"An error occurred:{e}", exc_info=True)
            self.session.abort_transaction()
            return {"success": False, "msg": f"{e}"}, 500



    @Logger.generate
    def get_chats(self, user_id, ignore_fields: dict = None, filter_fields: dict = None):
        """
        Retrieves all chats for a given user.

        :param user_id: The ID of the user whose chats are to be retrieved.
        :type user_id: str
        :param ignore_fields: A dictionary of fields to ignore chats by.
        :type ignore_fields: dict
        :param filter_fields: A dictionary of fields to filter chats by.
        :type filter_fields: dict
        :return: A dictionary with success status, list of chats, and HTTP status code.
        :rtype: tuple(dict, int)
        :raises Exception: If there is an error in retrieving the chats.
        """
        status, chats = self.mongo_chats.get_all_by_user_id(user_id)
        
        try:
            if chats:
                if ignore_fields:
                    chats = [chat for chat in chats if not all(chat.get(key) == value for key, value in ignore_fields.items())]
                if filter_fields:
                    chats = [chat for chat in chats if all(chat.get(key) == value for key, value in filter_fields.items())]
                chat_details = [{"chat_id": str(chat["_id"]), "chat_name": str(chat["chat_name"])} for chat in chats]
                logger.info("Successfully fetched chats")
                return {"success": True, "chats": chat_details, "msg": "Chats retrieved successfully."}, 200
            else:
                raise Exception(f"No chats found with user_id: {user_id}")
        except Exception as e:
            logger.error(str(e), exc_info=True)
            return  {"success": False, "msg": f"{e}"}, 500

    
    @Logger.generate
    def get_information(self, chat_id):
        """
        Retrieves detailed information for a specific chat.

        :param chat_id: The ID of the chat whose information is to be retrieved.
        :type chat_id: str
        :return: A dictionary with success status, chat details, and HTTP status code.
        :rtype: tuple(dict, int)
        :raises Exception: If there is an error in retrieving the chat information.
        """
        try:
            status, chat = self.mongo_chats.get_by_id(chat_id)
            
            if chat:
                logger.info("getting information from chats collection")
                metadata = []
                source_id = None
                columns = []
                cwf = chat.get("cwf") #{"source_id" : "34567890987654"}
                configurations=chat.get("configurations",{})
                if cwf:
                    source_id = cwf.get("source_id")
                if source_id:
                    cache = self.cache.get_item(source_id, chat['user_id'], chat_id)
                    if cache:
                        file_name = cache.get("file_name")
                        cwf["alias"] = cache.get("dataframe_alias",file_name)
                        cwf["type"] = cache.get("type")
                        if cache:
                            metadata = cache.get("metadata")
                            if metadata:
                                column_information = metadata.get("column_information")
                                if column_information:
                                    columns = column_information.get("column_names")
                                
                loaded_files=CommonUtils().get_chat_files_aliases_document(self.session,chat_id)
                mode = chat.get("job_mode")
                if not mode:
                    if chat.get("code"):
                        mode = JobModes.ACE.value
                    else:
                        mode = JobModes.LLM.value
                chat_details = {"cwf": cwf, "loaded_files": loaded_files, "metadata":columns,"configurations":configurations, "job_mode": mode}
                logger.info("fetched information from chats successfully")
                return {"success": True, "chats": chat_details, "msg": "Information retrieved successfully."}, 200
            else:
                return True, 204
        except Exception as e:
            logger.error(str(e), exc_info=True)
            return {"success": False, "msg": f"{e}"}, 500


    def _parse_pipeline_from_string(self, pipeline_str: str) -> List:
        yaml_data = yaml.safe_load(pipeline_str)
        json_string = json.dumps(yaml_data, indent=4)
        return json.loads(json_string)

    def _process_read_file_in_pipeline(self, pipeline_item, chat_item, user_id):
        output_file_name = pipeline_item.get('output', {}).get('dataframe_alias')
        output_source_id = pipeline_item.get('output', {}).get('source_id')
        
        param_file_id = pipeline_item.get('parameters', {}).get('file_id')
        
        # each file item in chat has source_id, alias, type
        chat_files = chat_item.get("files", [])
        user_files = self.mongo_files.get_by_user_id(user_id)
        
        # if file is already loaded in chat return
        item_exists = any([True for file in chat_files if file['source_id'] == output_source_id and file['alias'] == output_file_name])
        if item_exists:
            return None
        
        # if file belongs to user but not in chat, load the file in chat
        for file in user_files:
            if file['file_id'] == param_file_id:
                return file
        
        raise ValueError(f"File with file_id {param_file_id} does not belong to user_id {user_id}")
    
    # def _process_read_table_in_pipeline(self, pipeline_item, chat_item, user_id):
    #     table_name = pipeline_item.get('output', {}).get('dataframe_alias')
    #     source_id = pipeline_item.get('output', {}).get('source_id')

    #     for file_item in files:
    #         if file_item.get('source_id') == source_id:
    #             file_item['alias'] = table_name
    #             # TODO: Should use chat, user and source info for updating
    #             self.mongo_cache.update_one_by_source_id_value(source_id, 'dataframe_alias', table_name)
                
    #         if not any(f['source_id'] == file_item['source_id'] for f in new_files):
    #             new_files.append(file_item)
    
    def _handle_chat_update_code_mode(self, chat_id, req_data):
        code = req_data.get("value", "")
        self.mongo_chats.update_one(chat_id, "code", code)
        self.update_mode(chat_id, JobModes.ACE.value)
    
    def _handle_chat_update_yaml_mode(self, chat_id, req_data):
        json_history: List = self._parse_pipeline_from_string(req_data.get("value", "[]"))
        self.mongo_chats.update_one(chat_id, "history", json_history)
        self.mongo_chats.update_one(chat_id, "isChatMode", False )
        cwf, files = ChatUtils().get_cwf_and_files(json_history)
        self.mongo_chats.update_one(chat_id, "cwf", cwf)
        self.mongo_chats.update_one(chat_id, "files", files)
        self.update_mode(chat_id, JobModes.YAML.value)

    def _handle_chat_update_llm_mode(self, chat_id):
        self.update_mode(chat_id, JobModes.LLM.value)

    @Logger.generate
    def create_or_update_data(self, chat_id, req_data):
        """
        Creates or updates data for a specific chat.

        :param chat_id: The ID of the chat for which data is to be created or updated.
        :type chat_id: str
        :param req_data: The data to be created or updated for the chat.
        :type req_data: dict
        :param req_data['mode']: The mode of data processing. Can be either 'python' or 'yaml'.
        :type req_data['mode']: str
        :param req_data['value']: The data to be processed, which varies based on the mode.
            - If mode is 'python', this should be a string representing code.
            - If mode is 'yaml', this should be a YAML-formatted string representing pipeline history.
        :type req_data['value']: str
        :return: A tuple containing a dictionary with success status, chat details, and HTTP status code.
        :rtype: tuple(dict, int)
        :return: 
            - success (bool): Indicates whether the chat data was created or updated successfully.
            - chat_id (str): The ID of the chat for which the data was updated.
            - message (str): A message providing more information about the result of the operation.
        :raises Exception: If there is an error in creating or updating the data.
        """
        try:
            mode = req_data.get("mode")
            if mode == JobModes.ACE.value:
                self._handle_chat_update_code_mode(chat_id, req_data)
            elif mode == JobModes.YAML.value:
                self._handle_chat_update_yaml_mode(chat_id, req_data)
            elif mode == JobModes.LLM.value:
                self._handle_chat_update_llm_mode(chat_id)
            else:
                # Note: default case
                self._handle_chat_update_llm_mode(chat_id)
            return {
                "success": True,
                "chat_id": chat_id,
                "message": "Updated chat data"
            }, 201
        except Exception as e:
            logger.error(str(e), exc_info=True)
            return {"success": False, "msg": f"{e}"}, 500
    
    @Logger.generate
    def get_data(self, chat_id):
        """
        Retrieves data for a specific chat.

        :param chat_id: The ID of the chat whose data is to be retrieved.
        :type chat_id: str
        :return: A dictionary with success status, chat data, and HTTP status code.
        :rtype: tuple(dict, int)
        :raises Exception: If there is an error in retrieving the chat data.
        """
        status, chat = self.mongo_chats.get_by_id(chat_id)
        
        try:
            if chat:
                code = chat.get("code", "")
                pipeline_history = chat.get("history", [])
                for entry in pipeline_history:
                    groups = entry.get('parameters', {}).get('groups', [])
                    for group in groups:
                        if 'extra_info' in group:
                            del group['extra_info']
                yml_data = ""
                if pipeline_history:
                    yml_data = yaml.dump(pipeline_history, default_flow_style=False,indent=4)
                chat_details = {"code":code, "history":yml_data}
                logger.info("Successfully fetched chat data")
                return {"success": True, "chats": chat_details, "msg": "Chat data retrieved Successfully."}, 200
            else:
                raise Exception(f"No chat found with chat_id: {chat_id}")
        except Exception as e:
            logger.error(str(e), exc_info=True)
            return  {"success": False, "msg": f"{e}"}, 500
    
    def _invalidate_cache_for_chat(self, user_id, chat_id) -> None:
        # delete files entries from chat
        Chat(self.session).update(chat_id, "files", [])
        
        # delete all cache entries
        meta_processor = MetaProcessor(self.session)
        status, cache_docs = self.mongo_cache.get_all_by_user_id_key_value(user_id, "chat_id", chat_id)
        for doc in cache_docs:
            meta_processor.delete_files(chat_id, doc["source_id"], should_save_history=False)
        
        return
    
    def _rebuild_cache_with_history_for_chat(self, chat_id):
        success, _, _ = ReRunService(self.session).pipeline(chat_id, update_job_mode=False)
        if not success:
            logger.error(f"Failed to rebuild cache for chat {chat_id}")
    
    def update_mode(self, chat_id, job_mode):
        try:
            chat = Chat(self.session)
            valid_modes = {JobModes.ACE.value, JobModes.LLM.value, JobModes.YAML.value}

            if job_mode not in valid_modes:
                return {
                    "success": False,
                    "message": "mode not valid"
                }, 404
                
            success, chat_doc = chat.get(chat_id)
            if not success:
                return {
                    "success": False,
                    "message": f"Invalid chat id {chat_id}"
                }
            current_job_mode = chat_doc.get("job_mode", "")
            user_id = chat_doc.get("user_id")
            
            if current_job_mode == "":
                # No job mode set currently, simply set the input job mode
                pass
            elif current_job_mode == job_mode:
                # job mode is already same as passed job mode
                pass
            elif current_job_mode == "llm" and (job_mode == "yaml" or job_mode == "python"):
                # switching to a different mode, invalidate the chats
                # self._invalidate_cache_for_chat(user_id, chat_id)
                pass
            elif (current_job_mode == "yaml" or current_job_mode == "python") and job_mode == "llm":
                # rebuild cache based on current yaml
                self._rebuild_cache_with_history_for_chat(chat_id)

            chat.update_mode(chat_id, job_mode)
            return True, 204
        except Exception as e:
            logger.error(f"Failed to update job mode {e}", exc_info=True)
            return {"success": False, "message": "Failed to update job mode"}, 500
        