
from collections import OrderedDict
import os
from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase
from typing import Any, Optional, List, Tuple
import uuid
from .....models.connector import MongoConnector
from .....models.mongo.mongo_files import MongoFactory, MongoFiles
from ....extract.file_operations.read import Read
from .....exceptions.exception import *
from .....logger.logger import Logger, logger
from .....api.data.cache import Cache
from .....api.data.chat import Chat
from ....metadata.meta_processor import MetaProcessor
from .....configurations.api.config import BaseConfig
mongo = MongoConnector()
read = Read()

mongo_client = mongo.client

# [REVIEW] (added by pooja): This CreateDataframeDictionary is not called from anywhere. We need to re-check it's purpose.
class CreateDataframeDictionary:
    def __init__(self, session):
        self.session = session

    @Logger.generate
    def create(self, chat_id):
        try:
            dataframes_dict = {}
            logger.info(f"Creating dataframes for the chat: {chat_id}")
            chats = MongoFactory(mongo_client, "chats", session=self.session)
            get_success, chat_document = chats.get_by_id(chat_id)
            for file_info in chat_document["files"]:
                cache = get_cache(session=self.session)
                feather_files_document = cache.get_item(file_info["source_id"], chat_document["user_id"], chat_id)
                feather_success, dataframe = read.feather(feather_files_document["feather_file_path"])
                dataframes_dict.update({file_info["source_id"]: {"df":dataframe, "alias":file_info["alias"]}})
            logger.info(f"Returning dataframes dict..")
            logger.debug(f"dataframes_dict: {dataframes_dict}")
            return dataframes_dict
        except Exception as e:
            logger.error(f"Failed to create dataframes dictionaries due to {str(e)}.", exc_info=True)
            raise UtilsException(f"Failed to create dataframes dictionaries due to {str(e)}.") from e
        
class DataframeInformation:
    def __init__(self, config_dict= None, user_info = None, session=None):
        self.config_dict = OrderedDict(config_dict) if config_dict else OrderedDict()
        self.user_info = user_info if user_info else {}
        self.session=session
        self._meta_processor = MetaProcessor(session=self.session)

    def get(self, id=None, alias=None):
        try:
            if id and alias:
                if id in self.config_dict and self.config_dict[id].get('alias') == alias:
                    return self.config_dict[id]["df"]
                else:
                    raise Exception(f"ID '{id}' and Alias '{alias}' are either not registered or mismatched.")
            
            elif id:
                if id in self.config_dict:
                    return self.config_dict[id]["df"]
                else:
                    # In case this function was called without keyword argument and agent meant to pass alias, we have this fallback to check if id is meant as alias
                    matched_id = next((key for key, value in self.config_dict.items() if isinstance(value, dict) and value.get('alias') == id), None)
                    if matched_id:
                        return self.config_dict[matched_id]["df"]
                    raise Exception(f"ID '{id}' not found.")
            
            elif alias:
                id = next((key for key, value in self.config_dict.items() if isinstance(value, dict) and value.get('alias') == alias), None)
                if id:
                    return self.config_dict[id]["df"]
                else:
                    raise Exception(f"Alias '{alias}' not found.")
            
            else:  # if id is None and alias is None
                return self.config_dict
        
        except Exception as e:
            raise Exception(str(e)) from e
    
    def create(self, alias, dataframe, id=None):
        try:
            id_exists = False
            if id and id in self.config_dict:
                id_exists = True
                # Check if alias is already assigned to another id
                for key, value in self.config_dict.items():
                    if isinstance(value, dict):
                        if value.get('alias') == alias and key != id:
                            raise Exception(f"The alias '{alias}' is already assigned to another ID.")
            
            alias_exists = next((key for key, value in self.config_dict.items() if isinstance(value, dict) and value.get('alias') == alias), None)
            
            if alias_exists or id_exists:
                self.delete(alias)

            if not id:
                id  = str(uuid.uuid4())
            if self.config_dict.get("type") == "LLM":
                id = self.add_data_to_cache(dataframe, alias, id)
            self.config_dict[id] = {"df": dataframe, "alias": alias}
            data = {
                    "source_id": id,
                    "alias": alias
                }

            return data
        except Exception as e:
            raise Exception(str(e)) from e

    def update(self,  alias,dataframe, id=None):
        # TODO: This is error prone. We need to update cache in case of dataframe update as well.
        try:
            if id and alias:
                # Check if id and alias match as a key-value pair
                if self.config_dict.get(id, {}).get('alias') != alias:
                    raise Exception(f"ID '{id}' and Alias '{alias}' do not match.")
                else:
                    self.config_dict[id]['df'] = dataframe
                    return True
                

            # Find id based on alias
            id = next((key for key, value in self.config_dict.items() if isinstance(value, dict) and value.get('alias') == alias), None)
            if not id:
                return self.create(alias=alias, dataframe=dataframe)


            # Update dataframe
            self.config_dict[id]['df'] = dataframe
            
            if self.config_dict.get("type") == "LLM":
                self.update_cache_data(dataframe, alias, id)

            return True

        except Exception as e:
            raise Exception(str(e)) from e

    def delete(self, alias, id=None):
        try:

            if id and alias:
                # Check if id and alias match as a key-value pair
                if self.config_dict.get(id, {}).get('alias') != alias:
                    raise Exception(f"ID '{id}' and Alias '{alias}' do not match.")
                else:
                    if self.config_dict.get("type") == "LLM":
                        self.remove_existing_df_from_cache(alias, id)
                    self.config_dict.pop(id)
                    return True
            # Find id based on alias
            id = next((key for key, value in self.config_dict.items() if isinstance(value, dict) and value.get('alias') == alias), None)
            if not id:
                raise Exception(f"Alias '{alias}' is not registered.")
            # Remove entry from config_dict
            if self.config_dict.get("type") == "LLM":
                self.remove_existing_df_from_cache(alias, id)
            self.config_dict.pop(id)

            return True

        except Exception as e:
            raise Exception(str(e)) from e
    
    def remove_existing_df_from_cache(self, alias: str, source_id: Optional[str] = None) -> None:
        try:
            user_id, chat_id = self.user_info['user_id'], self.user_info['chat_id']
            cache_db, chat = Cache(self.session), Chat(self.session)
            
            cache: CacheBase = get_cache(session=self.session)
            if source_id:
                doc = cache.get_item(source_id, user_id, chat_id)
                file_path = doc.get("feather_file_path")
                cache_db.delete(doc.get("_id"))

                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        logger.info("Successfully deleted the files")
                    except PermissionError: # pragma: no cover
                        overall_message = "Failed to delete the feather file"
                        logger.error(overall_message, exc_info=True)

            success, chat_item = chat.get(chat_id)
            chat_item_files = chat_item.get("files")
            new_files = [file for file in chat_item_files if file['alias'] != alias]
            chat.update(chat_id, "files", new_files)
        except Exception as e:
            logger.info(str(e))
            raise RuntimeError("Failed to remove data from cache") from e
            
    def update_cache_data(self, df: Any, alias: str, id: str) -> int:
        try:
            user_id, chat_id = self.user_info['user_id'], self.user_info['chat_id']
            if not id:
                id = Cache(self.session).filter({"dataframe_alias": alias, "user_id": user_id, "chat_id": chat_id})

            # generate metadata_dict again and get feather_file_path of the item
            cache_db, chat = Cache(self.session), Chat(self.session)
            cache = get_cache(session=self.session)
            metadata_success, metadata_dict = self._meta_processor.generate_metadata(df)
            cache_item = cache.get_item(id, user_id, chat_id)
            feather_file_path = cache_item["feather_file_path"]
            status, path = self._meta_processor.upload_feather(feather_file_path, df)
            cache_db.update_one_by_fields(id, chat_id, user_id, "metadata", metadata_dict)
        except Exception as e:
            logger.error(str(e))
            raise RuntimeError("Failed to update cache") from e
            
    def add_data_to_cache(self, df: Any, alias: str, id: str) -> int:
        try:
            user_id, chat_id = self.user_info['user_id'], self.user_info['chat_id']
            cache, chat = Cache(self.session), Chat(self.session)
            metadata_success, metadata_dict = self._meta_processor.generate_metadata(df)
            feather_file_path = os.path.join(BaseConfig.BASE_DIR,BaseConfig.UPLOAD_FOLDER,user_id, ".cache", chat_id, str(uuid.uuid4()) + ".feather")
            copy_feather_file_path = os.path.join(BaseConfig.BASE_DIR,BaseConfig.UPLOAD_FOLDER,user_id, ".cache", chat_id, str(uuid.uuid4())+ "_copy" + ".feather")
            update_info = {
                "feather_file_path": feather_file_path,
                "file_name": alias,
                "metadata": metadata_dict,
                "export_path": None,
                "feather_copy": copy_feather_file_path,
                "export_name": None,
                "user_id": user_id,
                "chat_id": chat_id,
                "dataframe_alias": alias
            }
            
            status, path = self._meta_processor.upload_feather(feather_file_path, df)

            success, inserted_id = cache.create(update_info)
            cache.update(inserted_id, "source_id", id)

            chat_data=[{"source_id":id,"alias":alias}]
            new_data = chat.get(chat_id)[1]["files"] + chat_data
            chat.update(chat_id, "files", new_data)
            chat.update(chat_id, "cwf", chat_data)
            return id
        except Exception as e:
            logger.info(str(e))
            raise RuntimeError("Failed to add data to cache") from e
        
    def get_all_id_alias(self) -> List[Tuple]:
        """
        Returns a list of all id, alias set present in the DFInfo
        """
        data = []

        for key, value in self.config_dict.items():
            if not isinstance(value, dict):
                logger.warning(f"Dataframeinformation config dict has some values which are not dictionary - {self.config_dict}")
            else:
                if 'alias' not in value:
                    logger.warning(f"Some Dataframeinformation values don't have 'alias' info - {self.config_dict}")
                else:
                    data.append(
                        (key, value.get('alias'))
                    )
        return data
