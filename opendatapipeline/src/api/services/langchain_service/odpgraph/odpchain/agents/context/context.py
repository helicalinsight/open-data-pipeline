import pandas as pd
from src.logger.logger import Logger, logger
from src.api.services.langchain_service.odpgraph.odpchain.agents.context.context_model import ContextModel
from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase
from src.models.connector import MongoConnector
from src.models.mongo.mongo_factory import MongoFactory

mongo_connector = MongoConnector()
mongo_client=mongo_connector.client


class Context(ContextModel):
    # use only dataframe
    def __init__(self, session=None):
        try:
            super().__init__(session)
            self.session=session
            self.caches: CacheBase = get_cache(session=self.session)
            self.chats = MongoFactory(mongo_client, "chats", self.session)
        except Exception as e:
            logger.error(f"Error initializing Memory: {str(e)}", exc_info=True)
            raise Exception(f"Error initializing Memory: {str(e)}") from e
    
    def get_columns(self, chat_id):
        _,chat_doc=self.chats.get_by_id(chat_id)
        source_ids = []
        columns = []
        for file in chat_doc.get("files", []):
            source_ids.append(file["source_id"])
            _, cache_doc = self.caches.get_item(file["source_id"], chat_doc["user_id"], chat_id)
            columns.append(cache_doc["metadata"]["column_information"]["column_names"])
        return columns
    
    def get_metadata(self, chat_id):
        _,chat_doc=self.chats.get_by_id(chat_id)
        source_ids = []
        metadata = []
        for file in chat_doc.get("files", []):
            source_ids.append(file["source_id"])
            _, cache_doc = self.caches.get_item(file["source_id"], chat_doc["user_id"], chat_id)
            metadata.append(cache_doc["metadata"])
        return metadata
    
    def get_datatypes(self, chat_id):
        _,chat_doc=self.chats.get_by_id(chat_id)
        source_ids = []
        datatypes = []
        for file in chat_doc.get("files", []):
            source_ids.append(file["source_id"])
            _, cache_doc = self.caches.get_item(file["source_id"], chat_doc["user_id"], chat_id)
            datatypes.append(cache_doc["metadata"]["column_information"]["datatypes"])
        return datatypes
    
    def get_dataframes(self, chat_id):
        _,chat_doc=self.chats.get_by_id(chat_id)
        df_dict = {}
        logger.info(f"chat_doc[files] {chat_doc}")
        for file in chat_doc.get("files", []):
            logger.info(f"file[alias] {file}")
            cache_doc = self.caches.get_item(file["source_id"], chat_doc["user_id"], chat_id)
            path = cache_doc["feather_file_path"]
            df = pd.read_feather(path)
            df_dict[cache_doc["dataframe_alias"]] = df
        logger.info(f"df_dict {df_dict}")
        return df_dict

        
    def get_data_for_df(self, chat_id, table_name):
        logger.info("in get_data")
        _,chat_doc=self.chats.get_by_id(chat_id)
        df = None  # Initialize to handle empty or no-match conditions safely
        logger.info(f"chat_doc[files] {chat_doc}")
        for file in chat_doc.get("files", []):
            logger.info(f"file[alias] {file}")
            logger.info(f"table_name {table_name}")
            if file["alias"] == table_name or file["alias"] in table_name:
                cache_doc = self.caches.get_item(file["source_id"], chat_doc["user_id"], chat_id)
                logger.info(f"cache_doc {cache_doc}")
                path=cache_doc["feather_file_path"]
                logger.info(f"path {path}")
                df=pd.read_feather(path)
                logger.info(df)
        return df