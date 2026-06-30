from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ....etl.metadata.meta_processor import MetaProcessor
import os
import pandas

from ....logger.logger import Logger, logger
from ..rerun.service import ReRunService
from .utils import find_source_id



    
class UndoRedoService:
    """Service for managing undo and redo operations in chat history.

    This service allows users to undo or redo operations in chat history, adjusting the pipeline and updating the chat state accordingly.

    Attributes:
        session (Session): The database session used for operations.
        mongo_connector (MongoConnector): MongoDB connector instance.
        mongo_client (MongoClient): MongoDB client instance.
        chat_collection (MongoFactory): Collection handler for chat documents.
        cache_collection (MongoFactory): Collection handler for cache documents.

    Methods:
        undo(user_id, chat_id):
            Undoes the last operation in the chat history and updates the chat state.
        
        redo(user_id, chat_id):
            Redoes the next operation in the chat history and updates the chat state.
    """
    def __init__(self,session=None):
        """Initializes the UndoRedoService with a database session.

        Args:
            session (Session, optional): The database session to use for operations.
        """
        self.session=session
        self.mongo_connector = MongoConnector()
        self.mongo_client = self.mongo_connector.client
        self.chat_collection = MongoFactory(self.mongo_client, "chats", session=self.session)
    
    def undo(self,user_id, chat_id):
        """Undoes the last operation in the chat history and updates the chat state.

        Args:
            user_id (str): The ID of the user requesting the undo.
            chat_id (str): The ID of the chat where the undo operation is to be performed.

        Returns:
            tuple: A tuple containing a dictionary with status message and success flag, and the HTTP status code.

        Raises:
            Exception: If no undoable operations are available or if an error occurs during the process.
        """
        status_msg, chat = self.chat_collection.get_by_id(chat_id)
        if chat is None:
            return {"msg": "No step to undo", "success": True}, 200
        is_undoRedoAvailable = chat.get("is_undoRedoAvailable",True)
        try:
            if chat:
                chat_history = chat.get("history", None)
                chat_history = [item for item in chat_history if not item["function"].startswith(("export", "export_table", "step_export"))]
                if len(chat_history) == 0:
                    self.chat_collection.update_one(chat_id, "next", [])
                    return {"msg": "No step to undo", "success": True}, 200
                if len(chat_history) >= 1:
                    till_last_step=chat_history[:-1]
                    last_step = chat_history[-1]
                    pipeline_status, _, _ = ReRunService(self.session).pipeline(
                        chat_id, pipeline=till_last_step, update_job_mode=False)
                    if not pipeline_status:
                        logger.error("Failed to run pipeline for undo step")
                        return {"msg": "Undo Failed", "success": False}, 500
                    chatnext = [last_step]
                    
                    cwf = find_source_id(till_last_step)
                    if cwf is None:
                        cwf_update=None
                        self.chat_collection.update_one(chat_id, "cwf", cwf_update)
                        self.chat_collection.update_one(chat_id, "next", [])
                    else:
                        cwf_update={"source_id":cwf}
                        self.chat_collection.update_one(chat_id, "cwf", cwf_update)
                    
                    if len(chat.get("next", [])) > 0:
                        next_list = chatnext + chat.get("next")
                        self.chat_collection.update_one(chat_id, "next", next_list)
                    else:
                        self.chat_collection.update_one(chat_id, "next", chatnext)

                    
                    return {"msg" : "Undo Successful", "success" : True}, 200
            else:
                return {"msg" : "Chat not found", "success" : False}, 404

                            
        except Exception as e:
            logger.error(f"Failed to pefrom undo:  {e}", exc_info=True)
            status = False
            return {"msg" : "Undo Failed", "success" : False}, 404
        

    def redo(self,user_id, chat_id):
        """Redoes the next operation in the chat history and updates the chat state.

        Args:
            user_id (str): The ID of the user requesting the redo.
            chat_id (str): The ID of the chat where the redo operation is to be performed.

        Returns:
            tuple: A tuple containing a dictionary with status message and success flag, and the HTTP status code.

        Raises:
            Exception: If no redoable operations are available or if an error occurs during the process.
        """
        status_msg,chat = self.chat_collection.get_by_id(chat_id)
        is_undoRedoAvailable=chat.get("is_undoRedoAvailable",True)
        chat_next = chat.get("next", None)
        chat_history = chat.get("history", None)
        if len(chat_next) >= 1:
                new_next = chat_next[1:]
        else:
                new_next = []
        try:
                next_history = chat_next[0]
                chat_history.append(next_history)
                ReRunService(self.session).pipeline(chat_id, pipeline=chat_history)
                self.chat_collection.update_one(chat_id, "next", new_next)
                return {"msg" : "Redo Successfull", "success" : True}, 200
            
                
        except Exception as e:
                logger.error(str(e), exc_info=True)
                return {"msg" : "Redo Failed", "success" : False}, 404
           