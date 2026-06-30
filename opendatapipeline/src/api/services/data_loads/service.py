
from typing import List, Tuple
import uuid
from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase
from ....hooks.database_connector import DatabaseConnector
from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ....etl.metadata.meta_processor import MetaProcessor
from .utils import DataLoadsUtilities
from ....exceptions.exception import UtilsException, DatabaseConnectorException
from ....logger.logger import Logger, logger
from ...data.chat import Chat
from bson import ObjectId
from core.datasource.base import DBConnection
from core.datasource.implementations.s3 import S3
from src.hooks.database_connector import DatabaseConnector

db_connector = DatabaseConnector()

# {source:"file", details:{"file_id":"record._id","chat_id":"job id","type":"file_type","file_name":"file_name"}}
class DataLoadService:
    """
    Service class for loading data from files or databases into jobs.
    """
    def __init__(self, session, aod_audit_instance = None):
        """
        Initializes the DataLoadService with a MongoDB session, cache, and meta processor.

        :param session: The MongoDB session for transactions.
        :type session: pymongo.client_session.ClientSession
        """
        self.session=session
        self.mongo_connector = MongoConnector()
        self.mongo_client = self.mongo_connector.client
        self.meta_processor=MetaProcessor(self.session)
        self.mongo_chat = MongoFactory(self.mongo_client, "chats", session=self.session)
        self.mongo_connections = MongoFactory(self.mongo_client, "connections", session=self.session)
        self.cache: CacheBase = get_cache(session=self.session)
        self.aod_audit_instance = aod_audit_instance
    
    @Logger.generate
    def load_file_to_job(self, req_data):
        try:
            files_uploaded = []
            files_failed =[]
            status, req_data = DataLoadsUtilities().process_type_for_files(req_data)
            catalog = req_data.get("details", {}).get("catalog", {})
            catalog_list: List[Tuple] = list(catalog.items()) if catalog else ({},)
            chat_id = req_data.get("details", {}).get("chat_id")
            user_id = req_data.get("details", {}).get("user_id")
            for i in catalog_list:
                i = {i[0]: i[1]} if isinstance(i, tuple) else i
                req_data["details"]["catalog"] = i
                
                if status:
                    result, _source_id = self.meta_processor.execute(req_data["source"],**req_data["details"])
                    if result:
                        if chat_id is None or user_id is None:
                            raise ValueError("Missing chat_id or user_id")
                        feather_cache = self.cache.get_item(_source_id, user_id, chat_id)
                        alias = feather_cache.get("file_name", None)
                        file_type = feather_cache.get("type", None)
                        
                        if self.aod_audit_instance is not None:
                            try:
                                from opendatapipeline.src.etl.extract.file_operations.read import Read
                                _, df = self.aod_audit_instance.record(Read().feather)(feather_cache.get("feather_file_path"), old_df=None, step_name='read', audit_df_type="pandas")
                            except:
                                pass
                        else:
                            logger.warning(f"Got empty audit tracker instance for load_file_to_job, falling back to not tracking audit")
                        msg=f"{alias} loaded Successfully."
                        files_uploaded.append(msg)
                        logger.info("Files Loaded Successfully")
                    else:
                        logger.error("Failed to Load the file")
                        raise Exception(f"Failed to Load the file. req_data: {req_data}")
                else:
                    msg=f"Not able to process the file type"
                    logger.error("Not able to process the file type", exc_info=True)
                    raise Exception(f"Not able to process the file type. req_data: {req_data}")
            return {"success": True, "message": "Files Loaded Successfully", "files_uploaded":files_uploaded,"files_failed":files_failed}, 200
        except UtilsException as e:
            logger.error(f"{e}", exc_info=True)
            self.abort_transaction()
            return {"success": False, "message": f"{e}","files_uploaded":files_uploaded,"files_failed":files_failed}, 500

        except Exception as e: # pragma: no cover
            logger.error(f"{e}", exc_info=True)
            self.session.abort_transaction()
            return {"success": False, "message": f"{e} ","files_uploaded":files_uploaded,"files_failed":files_failed}, 500
    
    @Logger.generate
    def load_database_to_job(self, req_data):
        try:
            files_uploaded = []
            files_failed =[]
            status, data_load_list=DataLoadsUtilities().separate_catalog_with_file_name(req_data)
            chat_id = req_data.get("details", {}).get("chat_id")
            user_id = req_data.get("details", {}).get("user_id")
            if status:
                for data_load in data_load_list:
                    try:
                        result, source_id=self.meta_processor.execute(data_load["source"],**data_load["details"])
                        if result:
                            if chat_id is None or user_id is None:
                                raise ValueError("Expected non-null values for chat_id and user_id")
                            feather_cache = self.cache.get_item(source_id, user_id, chat_id)
                            alias = feather_cache.get("file_name", None)
                            file_type = feather_cache.get("type", None)
                            if self.aod_audit_instance is not None:
                                try:
                                    from opendatapipeline.src.etl.extract.file_operations.read import Read
                                    _, df = self.aod_audit_instance.record(Read().feather)(feather_cache.get("feather_file_path"), old_df=None, step_name='read', audit_df_type="pandas")
                                except:
                                    pass
                            else:
                                logger.warning(f"Got empty audit tracker instance for load_database_to_job, falling back to not tracking audit")
                            uploads = {"source_id": source_id, "alias": alias, "type": file_type}
                            msg=f"{data_load['details']['catalog']} loaded Successfully." 
                            files_uploaded.append(msg)
                        else:# pragma: no cover
                            raise Exception(f"Failed to Load the file. req_data: {req_data}")# pragma: no cover
                    except Exception as e:# pragma: no cover
                            msg=f"{data_load['details']['catalog']} : {e}"
                            files_failed.append(msg)
            else:# pragma: no cover
                raise Exception(f"Failed to Load the file. req_data: {req_data}")# pragma: no cover
            logger.info("Files Loaded Successfully")
            return {"success": True, "message": "Files Loaded Successfully","files_uploaded":files_uploaded,"files_failed":files_failed}, 200

        except DatabaseConnectorException as e:# pragma: no cover
            logger.error(f"{e}", exc_info=True)
            self.session.abort_transaction()
            return {"success": False, "message": e}, 500

        except UtilsException as e:# pragma: no cover
            logger.error(f"{e}", exc_info=True)
            self.session.abort_transaction()
            return {"success": False, "message": f"{e}"}, 500

        except Exception as e: # pragma: no cover
            logger.error(f"{e}", exc_info=True)
            self.session.abort_transaction()
            return {"success": False, "message": f"{e} "}, 500

    @Logger.generate
    def load_s3_file_to_job(self, req_data):
        try:
            files_uploaded = []
            files_failed = []

            details = req_data.get("details", {})
            connection_id = details.get("connection_id")
            file_name = details.get("file_name")
            file_type = details.get("type")
            chat_id = details.get("chat_id")
            user_id = details.get("user_id")
            catalog = details.get("catalog")
            status, data_load_list=DataLoadsUtilities().process_catalog_for_s3(req_data, file_name, file_type, catalog)
            if status:
                for data_load in data_load_list:
                    try:
                        result, source_id=self.meta_processor.execute(data_load["source"],**data_load["details"])
                        if result:
                            if chat_id is None or user_id is None:
                                raise ValueError("Expected non-null values for chat_id and user_id")
                            feather_cache = self.cache.get_item(source_id, user_id, chat_id)
                            alias = feather_cache.get("file_name", None)
                            file_type = feather_cache.get("type", None)
                            if self.aod_audit_instance is not None:
                                try:
                                    from opendatapipeline.src.etl.extract.file_operations.read import Read
                                    _, df = self.aod_audit_instance.record(Read().feather)(feather_cache.get("feather_file_path"), old_df=None, step_name='read', audit_df_type="pandas")
                                except:
                                    pass
                            else:
                                logger.warning(f"Got empty audit tracker instance for load_s3_file_to_job, falling back to not tracking audit")
                            uploads = {"source_id": source_id, "alias": alias, "type": file_type}
                            msg=f"{req_data['details']['catalog']} loaded Successfully." 
                            files_uploaded.append(msg)
                        else:# pragma: no cover
                            raise Exception(f"Failed to Load the file. req_data: {req_data}")# pragma: no cover
                    except Exception as e:# pragma: no cover
                            msg=f"{data_load['details']['catalog']} : {e}"
                            files_failed.append(msg)
            else:
                msg=f"Not able to process the file type"
                logger.error("Not able to process the file type", exc_info=True)
                raise Exception(f"Not able to process the file type. req_data: {req_data}")
            logger.info("Files Loaded Successfully")
            return {"success": True, "message": "Files Loaded Successfully","files_uploaded":files_uploaded,"files_failed":files_failed}, 200

        except DatabaseConnectorException as e:# pragma: no cover
            logger.error(f"{e}", exc_info=True)
            self.session.abort_transaction()
            return {"success": False, "message": e}, 500

        except UtilsException as e:# pragma: no cover
            logger.error(f"{e}", exc_info=True)
            self.session.abort_transaction()
            return {"success": False, "message": f"{e}"}, 500

        except Exception as e: # pragma: no cover
            logger.error(f"{e}", exc_info=True)
            self.session.abort_transaction()
            return {"success": False, "message": f"{e} "}, 500

    @Logger.generate
    def remove_file_from_job(self, req_data):
        try:
            chat_id = req_data.get("chat_id")
            source_id = req_data.get("source_id")
            result = self.meta_processor.delete_files(chat_id, source_id)
            return {"success": result, "message": "File Deleted Successfully"}, 200
        except Exception as e:
            logger.error(f"{e}", exc_info=True)
            self.session.abort_transaction()
            return {"success": False, "message": f"{e} "}, 500
