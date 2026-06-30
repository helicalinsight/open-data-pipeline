import json
import os
import re
import requests
from pydantic import BaseModel
from pydantic import Field
from src.api.services.execute.service import ExecuteService
import configparser
import difflib
from .........models.mongo.mongo_factory import MongoFactory
from .........models.connector import MongoConnector
from .utils import *
from .........logger.logger import logger, Logger
mongo_connector = MongoConnector()
config=configparser.ConfigParser()
mongo_client=mongo_connector.client
from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from pymongo import ReadPreference
wc_majority = WriteConcern("majority", wtimeout=1000)

mongo = MongoConnector()
mongo_client = mongo.client

class DataEngineeringWrapper(BaseModel):
    """Wrapper for AskonData API.

    This class provides methods to perform various data engineering operations
    such as renaming columns, adding columns, and trimming strings in a dataset.
    Each method sends a request to the AskonData API to execute the specified
    operation.

    :param query: JSON formatted string containing parameters for the operation
    :type query: str
    :param user_id: ID of the user requesting the operation
    :type user_id: str
    :param chat_id: ID of the chat associated with the operation
    :type chat_id: str
    :param session: Session object used for making API requests
    :type session: object
    """

    @Logger.generate
    def rename_columns(self, query: str, user_id, chat_id, session) -> str:
        """Renames columns in a dataset.

        :param query: JSON formatted string containing 'old_name' and 'new_name'
        :type query: str
        :param user_id: ID of the user requesting the operation
        :type user_id: str
        :param chat_id: ID of the chat associated with the operation
        :type chat_id: str
        :param session: Session object used for making API requests
        :type session: object
        :return: Result of the rename operation
        :rtype: str
        """
        logger.info(f"query: {query}")
        params = json.loads(query)
        logger.info(f"params details: {params}")
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "rename_columns"
        old_name = None
        new_name = None
        extra_info = None
        if params.get("old_name") not in ["", None] and params.get("new_name")  not in ["", None]:
            old_name = params.get("old_name") if isinstance(params.get("old_name"), str) else None
            new_name = params.get("new_name") if isinstance(params.get("new_name"), str) else None
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "old_name": old_name,
                    "new_name": new_name,
                    "extra_info": extra_info
                }
            ]
        }
        logger.info(f"parameters: {parameters}")
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        
        logger.info(f"wrapper details: {data}")
        try:
            headers = {
                "Content-Type": "application/json"
            }
            response = ExecuteService(session).execute(data)
            logger.info(f"response of rename_columns: {response}")
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}

    @Logger.generate
    def add_columns(self, query: str, user_id, chat_id, session) -> str:
        """Adds columns to a dataset.

        :param query: JSON formatted string containing 'columns' and 'default'
        :type query: str
        :param user_id: ID of the user requesting the operation
        :type user_id: str
        :param chat_id: ID of the chat associated with the operation
        :type chat_id: str
        :param session: Session object used for making API requests
        :type session: object
        :return: Result of the add columns operation
        :rtype: str
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}

        intent_name = "add_columns"
        columns = None
        default = None
        extra_info = None
        if params.get("columns") != "" and params.get("columns") != None:
            columns = params.get("columns") if isinstance(params.get("columns"), list) else [params.get("columns")]

        if params.get("default") != "" and params.get("default") != None:
            default = params.get("default") if isinstance(params.get("default"), (str, int, bool, float)) else (params.get("default") if isinstance(params.get("default"), list) else None)

        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "columns": columns,
                    "default": default,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters": parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}

    @Logger.generate
    def trim(self, query: str, user_id, chat_id, session) -> str:
        """Trims characters from columns in a dataset.

        :param query: JSON formatted string containing 'columns', 'number_of_characters', and 'location'
        :type query: str
        :param user_id: ID of the user requesting the operation
        :type user_id: str
        :param chat_id: ID of the chat associated with the operation
        :type chat_id: str
        :param session: Session object used for making API requests
        :type session: object
        :return: Result of the trim operation
        :rtype: str
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "trim"
        columns = None
        number_of_characters = None
        location = None
        extra_info = None
        if params.get("columns") != "" and params.get("columns") != None:
            columns = params.get("columns") if isinstance(params.get("columns"), list) else [
            params.get("columns")]
        if params.get("number_of_characters") not in [None, ""]:   
            number_of_characters = params.get("number_of_characters") if isinstance(params.get("number_of_characters"), int) else None

        if params.get("location") in ["left", "right"] and params.get("location") != "":    
            location = params.get("location") if isinstance(params.get("location"), str) else "left"
            
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "number_of_characters": number_of_characters,
                    "location": location,
                    "columns": columns,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}

    @Logger.generate
    def drop_columns(self, query: str, user_id, chat_id, session) -> str:
        """
        Drops the specified columns from the dataset.
        
        Args:
            query (str): JSON string containing 'columns' under 'columns' key.

        Returns:
            str: JSON response indicating success or failure with the result of the drop_columns operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "drop_columns"
        columns = None
        extra_info = None
        if params.get("columns"):
            if None not in params.get("columns") and "" not in params.get("columns") and params.get("columns") != []:
                columns = params.get("columns") if isinstance(params.get("columns"), list) else [
                    params.get("columns")]
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "columns": columns,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters": parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}

    @Logger.generate
    def drop_all_except_columns(self, query: str, user_id, chat_id, session) -> str:
        """
        Drop all columns except the specified columns from the dataset.

        :param query: JSON string containing the column names to retain.
        :type query: str
        :param user_id: The user ID requesting the operation.
        :type user_id: str
        :param chat_id: The chat ID of the session.
        :type chat_id: str
        :param session: The session object for executing the request.
        :type session: :class:`session`
        :return: A dictionary with the success status and the result of the operation.
        :rtype: dict
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "drop_all_columns_except"
        columns = None
        extra_info = None
        if params.get("columns") not in ["", None, []] and None not in params.get("columns") and "" not in params.get("columns"):
            columns = params.get("columns") if isinstance(params.get("columns"), list) else [params.get("columns")]
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "columns": columns,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters": parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}

    @Logger.generate
    def cast(self, query: str, user_id, chat_id, session) -> str:
        """
        Change the data type of specified columns.

        :param query: JSON string containing the column names and their new data types.
        :type query: str
        :param user_id: The user ID requesting the operation.
        :type user_id: str
        :param chat_id: The chat ID of the session.
        :type chat_id: str
        :param session: The session object for executing the request.
        :type session: :class:`session`
        :return: A dictionary with the success status and the result of the operation.
        :rtype: dict
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "typecast"
        columns = None
        old_type = None
        new_type = None
        extra_info = None
        if params.get("columns") not in ["", None]:
            columns = params.get("columns") if isinstance(params.get("columns"), list) else [params.get("columns")]
        if params.get("old_type") not in ["", None]:
            old_type = params.get("old_type") if isinstance(params.get("old_type"), str) else str(
                params.get("old"))
        if params.get("new_type") not in ["", None]:
            new_type = params.get("new_type") if isinstance(params.get("new_type"), str) else str(
                params.get("new_type"))
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "columns": columns,
                    "new_type": new_type,
                    "old_type": old_type,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}


    @Logger.generate
    def replace_special_characters(self, query: str, user_id, chat_id, session) -> str:
        """
        Replace special characters in the specified column with a new character.

        :param query: JSON string containing the column name and the characters to replace.
        :type query: str
        :param user_id: The user ID requesting the operation.
        :type user_id: str
        :param chat_id: The chat ID of the session.
        :type chat_id: str
        :param session: The session object for executing the request.
        :type session: :class:`session`
        :return: A dictionary with the success status and the result of the operation.
        :rtype: dict
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "replace_special_characters"
        source_column = None
        target_character = None
        replacement_character = None
        extra_info = None
        if params.get("columns") not in ["", None]:
            source_column = params.get("columns") if isinstance(params.get("columns"), list) else [params.get("columns")]

        if params.get("target_character") not in ["", None]:
            target_character = params.get("target_character") if isinstance(params.get("target_character"), str) else None

        if params.get("replacement_character") not in ["", None]:
            replacement_character = params.get("replacement_character") if isinstance(params.get("replacement_character"), str) else None
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "columns": source_column,
                    "target_character": target_character,
                    "replacement_character": replacement_character,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}

    @Logger.generate
    def split(self, query: str, user_id, chat_id, session) -> str:
        """
        Splits a source column into multiple destination columns based on a delimiter.

        Args:
            query (str): JSON string containing 'column', 'destination_columns', and 'delimiter'.
            user_id (str): The ID of the user.
            chat_id (str): The ID of the chat.
            session: The current session object.

        Returns:
            str: JSON response indicating success or failure with the result of the split operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "split"
        source_column = None
        split_columns = None
        delimiter = None
        extra_info = None
        if params.get("column") != "" and params.get("column") != None:
            source_column = params.get("column") if isinstance(params.get("column"), str) else None

        if params.get("destination_columns") not in ["", None, []] and None not in params.get("destination_columns") and "" not in params.get("destination_columns"):
            split_columns = params.get("destination_columns") if isinstance(params.get("destination_columns"), list) else [
            params.get("destination_columns")]
        
        if params.get("delimiter") != "" and params.get("delimiter") != None:
            delimiter = params.get("delimiter") if isinstance(params.get("delimiter"), str) else None
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "column": source_column,
                    "destination_columns": split_columns,
                    "delimiter": delimiter,
                    "extra_info": extra_info
				}
			]
		}
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}

    @Logger.generate
    def concat(self, query: str, user_id, chat_id, session) -> str:
        """
        Concatenates multiple columns into a single column with a specified separator.

        Args:
            query (str): JSON string containing 'columns', 'separator', and 'destination_column'.
            user_id (str): The ID of the user.
            chat_id (str): The ID of the chat.
            session: The current session object.

        Returns:
            str: JSON response indicating success or failure with the result of the concat operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "concat"
        columns = None
        separator = None
        destination_column = None
        extra_info = None
        if params.get("columns") not in ["", None, []] and None not in params.get("columns") and "" not in params.get("columns"):
            columns = params.get("columns") if isinstance(params.get("columns"), list) else [params.get("columns")]
        if params.get("separator") != "":
            separator = params.get("separator") if isinstance(params.get("separator"), str) else None
        if params.get("destination_column") != "":
            destination_column = params.get("destination_column") if isinstance(params.get("destination_column"), str) else None
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "columns": columns,
                    "separator": separator,
                    "destination_column": destination_column,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters": parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}

    @Logger.generate
    def deduplicate(self, query: str, user_id, chat_id, session) -> str:
        """
        Removes duplicate rows based on specified columns.

        Args:
            query (str): JSON string containing 'columns'.
            user_id (str): The ID of the user.
            chat_id (str): The ID of the chat.
            session: The current session object.

        Returns:
            str: JSON response indicating success or failure with the result of the deduplicate operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "deduplicate"
        columns = None
        extra_info = None
        if params.get("columns") not in ["", None, []] and None not in params.get("columns") and "" not in params.get("columns"):
            columns = params.get("columns") if isinstance(params.get("columns"), list) else [params.get("columns")]
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "columns": columns,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters": parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}


    @Logger.generate
    def filter_data(self, query: str, user_id, chat_id, session) -> str:
        """
        Filters data based on specified columns, expression, and values.

        Args:
            query (str): JSON string containing 'columns' under 'columns' key, 'expr' under 'expr' key and 'value' under 'value' key.

        Returns:
            str: JSON response indicating success or failure with the result of the filter operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "filter_value"
        expr = None
        columns = None
        value = None
        extra_info = None
        if isinstance(params.get("columns"), str) and params.get("columns") != "":
            columns = [params.get("columns")]
        elif isinstance(params.get("columns"), list):
            if params.get("columns") not in ["", None, [], [None], [""]]:
                columns = params.get("columns")
        if params.get("expr") != "":
            expr = params.get("expr") if isinstance(params.get("expr"), str) else None
        
        if isinstance(params.get("value"), (str,int,bool,float)) and params.get("value") != "":
            value = [params.get("value")]
        elif isinstance(params.get("value"), list):
            if params.get("value") not in ["", None, []] and None not in params.get("value") and "" not in params.get("value"):
                value = params.get("value")
        
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "columns": columns,
                    "expr": expr,
                    "value": value,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters": parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
           logger.error("An error occurred: %s", e, exc_info=True)
           return {"success":False,"result":response[0]}


    @Logger.generate
    def sort(self, query: str, user_id, chat_id, session) -> str:
        """
        Sorts the specified columns based on order (ascending/descending).

        Args:
            query (str): JSON data containing 'columns' under 'columns' key and 'ascending' under 'ascending' key.

        Returns:
            str: JSON response indicating success or failure with the result of the sort operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "sort"
        columns = None
        ascending = None
        extra_info = None
        if params.get("columns") != "" and params.get("columns") != None:
            columns = params.get("columns") if isinstance(params.get("columns"), list) else [
            params.get("columns")]

        if params.get("ascending") in [True ,False] and params.get("ascending") != "":
            ascending = params.get("ascending") if isinstance(params.get("ascending"), bool) else True
        
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "columns": columns,
                    "ascending": ascending,
                    "extra_info": extra_info
				}
			]
		}
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}

    @Logger.generate
    def lowercase(self, query: str, user_id, chat_id, session) -> str:
        """
        Converts the specified columns' values to lowercase.

        Args:
            query (str): JSON data containing 'columns' under 'columns' key.

        Returns:
            str: JSON response indicating success or failure with the result of the lowercase operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "lower_case"
        columns = None
        extra_info = None
        if params.get("columns") not in ["", None, []] and None not in params.get("columns") and "" not in params.get("columns"):
            columns = params.get("columns") if isinstance(params.get("columns"), list) else [params.get("columns")]
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        
        parameters = {
            "groups": [
                {
                    "columns": columns,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}


    @Logger.generate
    def uppercase(self, query: str, user_id, chat_id, session) -> str:
        """
        Converts the specified columns' values to uppercase.

        Args:
            query (str): JSON data containing 'columns' under 'columns' key.

        Returns:
            str: JSON response indicating success or failure with the result of the uppercase operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "upper_case"
        columns = None
        extra_info = None
        if params.get("columns") not in ["", None, []] and None not in params.get("columns") and "" not in params.get("columns"):
            columns = params.get("columns") if isinstance(params.get("columns"), list) else [params.get("columns")]
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "columns": columns,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}


    @Logger.generate
    def joins(self, query: str, user_id, chat_id, session) -> str:
        """
        Performs a join operation on the specified data files.

        Args:
            query (str): JSON string containing 'join_type', 'right_on', 'left_on', and 'file_names'.
            user_id (str): The ID of the user.
            chat_id (str): The ID of the chat.
            session: The current session object.

        Returns:
            str: JSON response indicating success or failure with the result of the join operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "joins"
        join_type = None
        right_on = None
        left_on = None
        file_names = None
        extra_info = None
        if params.get("join_type") != "":
            join_type = params.get("join_type") if isinstance(params.get("join_type"), str) else None
        if isinstance(params.get("right_on"), str) and params.get("right_on") != "":
            right_on = [params.get("right_on")]
        elif isinstance(params.get("right_on"), list):
            if params.get("right_on") not in ["", None, []] and None not in params.get("right_on") and "" not in params.get("right_on"):
                right_on = params.get("right_on")
        if isinstance(params.get("left_on"), str) and params.get("left_on") != "":
            left_on = [params.get("left_on")]
        elif isinstance(params.get("left_on"), list):
            if params.get("left_on") not in ["", None, []] and None not in params.get("left_on") and "" not in params.get("left_on"):
                left_on = params.get("left_on")
        if params.get("file_names") not in ["", None, []] and None not in params.get("file_names") and "" not in params.get("file_names"):
            file_names = params.get("file_names") if isinstance(params.get("file_names"), list) else [params.get("file_names")]
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        chats = MongoFactory(mongo_client, "chats", session)
        status_msg, chat = chats.get_by_id(chat_id)
        cache: CacheBase = get_cache(session=session)
        
        files = chat.get("files", [])
        file_informations=[]
        files_loaded_to_chat = [file.get("source_id") for file in files if file.get("source_id")]
        file_names_join=[]
        for id in files_loaded_to_chat:
            cache_doc = cache.get_item(id, user_id, chat_id)
            data={"alias":cache_doc.get('dataframe_alias'), "source_id":id}
            file_names_join.append(cache_doc.get('dataframe_alias', ""))
            file_informations.append(data)
        source_ids = []
        updated_file_names = []
        try:
            for file in file_names:

                file_name = difflib.get_close_matches(file, file_names_join, n=1, cutoff=0.9)
                if file_name != []:
                    updated_file_names.append(file_name[0])
                    source_id = next((file_info["source_id"] for file_info in file_informations if file_info["alias"] == file_name[0]), None)
                    source_ids.append(source_id)
                else:
                    raise Exception(f"File not found with query: {query}, user_id: {user_id} and chat_id: {chat_id}")
        except Exception as e:
            return f"Operation completed with an exception, please make sure you have the files uploaded: {str(e)}"
        parameters = {
            "groups": [
                {
                    "join_type": join_type,
                    "left_on": left_on,
                    "right_on": right_on,
                    "extra_info": extra_info
                }
            ],
            "file_names": updated_file_names,
            "source_id": source_ids
            }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}

    @Logger.generate
    def union(self, query: str, user_id, chat_id, session) -> str:
        """
        Performs a union operation on the specified data files.

        Args:
            query (str): JSON string containing 'columns' and 'file_names'.
            user_id (str): The ID of the user.
            chat_id (str): The ID of the chat.
            session: The current session object.

        Returns:
            str: JSON response indicating success or failure with the result of the union operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "union"
        columns = None
        cache: CacheBase = get_cache(session=session)
        file_names = None
        extra_info = None
        if params.get("columns"):
            if params.get("columns") not in ["", None, [], [""], [None]] and None not in params.get(
                    "columns") and "" not in params.get("columns"):
                columns = params.get("columns") if isinstance(params.get("columns"), list) else [
                    params.get("columns")]
        if params.get("file_names") not in ["", None, [], [""], [None]] and None not in params.get("file_names") and "" not in params.get("file_names"):
            file_names = params.get("file_names") if isinstance(params.get("file_names"), list) else [params.get("file_names")]
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        chats = MongoFactory(mongo_client, "chats", session)
        status_msg, chat = chats.get_by_id(chat_id)
        files = chat.get("files", [])
        files_loaded_to_chat = [file.get("source_id") for file in files if file.get("source_id")]
        file_names_union=[]
        file_informations=[]
        for id in files_loaded_to_chat:
            cache_doc = cache.get_item(id, user_id, chat_id)
            data={"alias":cache_doc.get('dataframe_alias'), "source_id":id}
            file_names_union.append(cache_doc.get('dataframe_alias', ""))
            file_informations.append(data)
        source_ids = []
        updated_file_names = []
        used_matches = set()
        try:
            for file in file_names:
                possible_matches = [f for f in file_names_union if f not in used_matches]
                best_match = difflib.get_close_matches(file, possible_matches, n=1, cutoff=0.9)
                if best_match:
                    matched_file = best_match[0]
                    used_matches.add(matched_file)
                    updated_file_names.append(matched_file)
                    source_id = next((info['source_id'] for info in file_informations if info['alias'] == matched_file), None)
                    source_ids.append(source_id)
        except Exception as e:
            return f"Operation completed with an exception, please make sure you have the files uploaded: {str(e)}"
        parameters = {
            "groups": [
                {
                    "columns": columns,
                    "extra_info": extra_info
                },
            ],
            "source_id": source_ids,
            "file_names": updated_file_names
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}
    
    @Logger.generate
    def aggregations(self, query: str, user_id, chat_id, session) -> str:
        """
        Performs an aggregation operation on the specified data columns.

        Args:
            query (str): JSON string containing 'agg', 'destination_columns', 'columns', and 'group_by'.
            user_id (str): The ID of the user.
            chat_id (str): The ID of the chat.
            session: The current session object.

        Returns:
            str: JSON response indicating success or failure with the result of the aggregation operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "aggregate"
        agg = None
        new_column = []
        source_column = None
        extra_info = None
        group_by = []
        if params.get("agg") not in ["", None, []] and None not in params.get("agg") and "" not in params.get("agg"):
            agg = params.get("agg") if isinstance(params.get("agg"), list) else [
                params.get("agg")]
            if params.get("columns") not in ["", None, []] and None not in params.get("columns") and "" not in params.get("columns"):  
                agg_funcs = params.get("agg")
                columns = params.get("columns")
                new_column = [f"{agg_func}_{src_col}" for src_col in columns for agg_func in agg_funcs]

        if params.get("destination_columns") not in ["", None, []] and None not in params.get("destination_columns") and "" not in params.get("destination_columns"):
            new_column = params.get("destination_columns") if isinstance(params.get("destination_columns"), list) else [
                params.get("destination_columns")]
            
        if params.get("columns") not in ["", None, []] and None not in params.get("columns") and "" not in params.get("columns"):
            source_column = params.get("columns") if isinstance(params.get("columns"), list) else [
                params.get("columns")]
            
        if params.get("group_by") not in ["", None, []] and None not in params.get("group_by") and "" not in params.get("group_by"):
            group_by = params.get("group_by") if isinstance(params.get("group_by"), list) else [
                params.get("group_by")]
            
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None

        parameters = {
            "groups": [
                {
                    "columns": source_column,
                    "destination_columns": new_column,
                    "agg": agg,
                    "group_by": group_by,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}
    
    @Logger.generate
    def date_format(self, query: str, user_id, chat_id, session) -> str:
        """
        Formats the date columns in the specified data files.

        Args:
            query (str): JSON string containing 'columns' and 'format'.
            user_id (str): The ID of the user.
            chat_id (str): The ID of the chat.
            session: The current session object.

        Returns:
            str: JSON response indicating success or failure with the result of the date format operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "date_format"
        columns = None
        format = None
        extra_info = None
        if isinstance(params.get("columns"), str) and params.get("columns") != "":
            columns = [params.get("columns")]
        elif isinstance(params.get("columns"), list):
            if params.get("columns") not in ["", None, [], [None], [""]]:
                columns = params.get("columns")
        if params.get("format") != "":
            format = params.get("format") if isinstance(params.get("format"), str) else None
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "columns": columns,
                    "format": format,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters": parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}

    @Logger.generate
    def arithmetic(self, query: str, user_id, chat_id, session) -> str:
        """
        Executes an arithmetic expression on specified data files.

        Args:
            query (str): JSON string containing 'query' and 'destination_column'.
            user_id (str): The ID of the user.
            chat_id (str): The ID of the chat.
            session: The current session object.

        Returns:
            str: JSON response indicating success or failure with the result of the arithmetic operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "expression"
        query = None
        destination_column = None
        extra_info = None
        if params.get("query") not in ["", None]:
            query = params.get("query") if isinstance(params.get("query"), str) else str(
                params.get("query"))
        if params.get("destination_column") not in ["", None]:
            destination_column = params.get("destination_column") if isinstance(params.get("destination_column"), str) else str(
                    params.get("destination_column"))
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "query": query,
                    "destination_column": destination_column,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}
        
    @Logger.generate
    def correlation(self, query: str, user_id, chat_id, session) -> str:
        """
        Calculates the correlation between specified columns in the data files.

        Args:
            query (str): JSON string containing 'columns' and 'destination_column'.
            user_id (str): The ID of the user.
            chat_id (str): The ID of the chat.
            session: The current session object.

        Returns:
            str: JSON response indicating success or failure with the result of the correlation calculation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "correlation"
        columns = None
        destination_column = None
        extra_info = None
        if params.get("columns") not in ["", None, []] and None not in params.get("columns") and "" not in params.get("columns"):
            columns = params.get("columns") if isinstance(params.get("columns"), list) else [params.get("columns")]
        if params.get("destination_column") != "":
            destination_column = params.get("destination_column") if isinstance(params.get("destination_column"), str) else None
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "columns": columns,
                    "destination_column": destination_column,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters": parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}

    @Logger.generate
    def rearrange_columns(self, query:str,user_id,chat_id, session)-> str:  
        """
        Rearranges the columns according to the column metadata and the specified input columns.

        Args:
            query (str): JSON string containing 'columns' under 'columns' key.

        Returns:
            str: JSON response indicating success or failure with the result of the rearrange_column operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "rearrange_columns"
        columns = None
        extra_info = None
        if params.get("columns") not in ["", None, []] and None not in params.get("columns") and "" not in params.get("columns"):
            columns = params.get("columns") if isinstance(params.get("columns"), list) else [params.get("columns")]
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "columns": columns,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}
    
    @Logger.generate
    def sql_operations(self, query:str,user_id,chat_id, session)-> str:  
        params = json.loads(query)
        
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "sql"
        query = None
        extra_info = None
        if params.get("query") not in ["", None]:
            query = params.get("query") if isinstance(params.get("query"), str) else str(
                params.get("query"))
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "query": query,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}
        
    @Logger.generate
    def pytool(self, query:str,user_id,chat_id, session, spk_code="<code></code>", df=None, df_alias=None, df_info=None)-> str: 
        """
        Executes Python code using the specified Spark code as context.

        Args:
            query (str): String containing the Python code wrapped in <code> tags.
            user_id (str): The ID of the user.
            chat_id (str): The ID of the chat.
            session: The current session object.
            spk_code (str): String containing the Spark code wrapped in <code> tags (default is "<code></code>").

        Returns:
            str: JSON response indicating success or failure with the result of the Python code execution.
        """
        logger.info(f"query {query}")
        code = query
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "pytool"
        try:
            #code=extract_code(code)
            logger.info(f"code {code}")
            logger.info(f"df {type(df)}")
            spk_code=extract_code(spk_code)
            logger.info(f"spk_code {spk_code}")
            #spk_code=match_aliases(code, spk_code)
            #logger.info(f"spk_code {spk_code}")
        except Exception as e:
            return {"success":False,"result":e}
        parameters = {
                "code": code ,
                "spark_code":spk_code,
                "df": df,
                "df_alias": df_alias,
                "df_info": df_info
        }
        logger.info(f"parameters {parameters}")
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        logger.info(f"data {data}")
        try:
            response = ExecuteService(session).execute(data)
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response}
    
    @Logger.generate
    def when_otherwise(self, query:str,user_id, chat_id, session)-> str:  
        """
        Prepares a SELECT query to handle the CASE expression based on specified conditions along with all columns.

        Args:
            query (str): JSON string containing the 'query' under 'query' key.

        Returns:
            str: JSON response indicating success or failure with the result of the when-otherwise operation.
        """
        query=query.replace('\n\t',' ').replace('\n',' ').replace('\t',' ')
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "when_otherwise"
        query = None
        extra_info = None
        if params.get("query") not in ["", None]:
            query = params.get("query") if isinstance(params.get("query"), str) else str(
                params.get("query"))
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "query": query,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}

    @Logger.generate
    def extract(self, query: str, user_id, chat_id, session) -> str:
        """
        Extracts specified components from a column in the data files.

        Args:
            query (str): JSON string containing 'column', 'component', and 'destination_column'.
            user_id (str): The ID of the user.
            chat_id (str): The ID of the chat.
            session: The current session object.

        Returns:
            str: JSON response indicating success or failure with the result of the extraction operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "extract"
        column = None
        component = None
        destination_column = None
        extra_info = None
        if params.get("column") != "":
            column = params.get("column") if isinstance(params.get("column"), str) else None
        if params.get("component") != "":
            component = params.get("component") if isinstance(params.get("component"), list) else ([params.get("component")] if isinstance(params.get("component"), str) else None)
        if params.get("destination_column") not in ["", None]:
            destination_column = params.get("destination_column") if isinstance(params.get("destination_column"), str) else None
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "column": column,
                    "component": component,
                    "destination_column": destination_column,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters": parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}

    def current_working_file(self, query: str, user_id, chat_id, session) -> str:
        """
        Set the current working file based on a query.

        Args:
            query (str): JSON string containing the file name to be matched.
            user_id: The ID of the user.
            chat_id: The ID of the chat.
            session: The current session object.

        Returns:
            str: JSON response indicating success or failure with the result of the operation.
        """
        try:
            params = json.loads(query)
            mongo_chats = MongoFactory(mongo_client, "chats", session)
            cache: CacheBase = get_cache(session=session)
            succ, chat = mongo_chats.get_by_id(chat_id)
            files = chat.get("files", [])
            fileNamedict = {}
            if len(files) >= 1:
                for file in files:
                    source_id=file["source_id"]
                    cache_file = cache.get_item(source_id, user_id, chat_id)
                    fileNamedict[source_id] = cache_file["file_name"]
            result = find_closest_match(params.get("file",""),fileNamedict, n=1, cutoff=0.7)
           
            if result:
                mongo_chats.update_one(chat_id, "cwf", {"source_id":result[0]})
                return {"success":True,"result":{"text":f"Operation completed: {result[1]} is selected as current working file"}}
            
            return {"success":False,"result":{"text":f"Operation completed with exception: {params.get('file')} does not match any file name"}}
        except:
            return {"success":False,"result":{"text":f"Operation completed with exception: {params.get('file')} does not match any file name"}}
  
            
    @Logger.generate
    def drop_na(self, query:str,user_id,chat_id, session)-> str:  
        """
        Drop missing values from the dataset based on the provided subset.

        Args:
            query (str): JSON string containing the subset of columns to consider.
            user_id: The ID of the user.
            chat_id: The ID of the chat.
            session: The current session object.

        Returns:
            str: JSON response indicating success or failure with the result of the drop operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "drop_na"
        subset = None
        extra_info = None
        if params.get("subset") not in ["", None, []] and None not in params.get("subset") and "" not in params.get("subset"):
            subset = params.get("subset") if isinstance(params.get("subset"), list) else [params.get("subset")]
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "subset": subset,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data)
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}
            

    @Logger.generate
    def fill_na(self, query: str, user_id, chat_id, session) -> str:
        """
        Fill missing values in the dataset based on provided parameters.

        Args:
            query (str): JSON string containing the parameters for filling missing values.
            user_id: The ID of the user.
            chat_id: The ID of the chat.
            session: The current session object.

        Returns:
            str: JSON response indicating success or failure with the result of the fill operation.
        """
        params = json.loads(query)
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "fill_na"
        column = None
        value = None
        method = None
        axis = None
        limit = None
        extra_info = None
        if params.get("column") != "":
            column = params.get("column") if isinstance(params.get("column"), str) else None
        if params.get("value") != "":
            value = params.get("value") if isinstance(params.get("value"), (str, int, float, bool)) else None
        if params.get("method") != "":
            method = params.get("method") if isinstance(params.get("method"), str) else None
        if params.get("axis") != "":
            axis = params.get("axis") if isinstance(params.get("axis"), (str, int)) else None
        if params.get("limit") != "":
            limit = params.get("limit") if isinstance(params.get("limit"), int) else None
        if params.get("extra_info") != "" and params.get("extra_info") != None:
            extra_info = params.get("extra_info") if isinstance(params.get("extra_info"), str) else None
        parameters = {
            "groups": [
                {
                    "column": column,
                    "value": value,
                    "method": method,
                    "limit": limit,
                    "axis": axis,
                    "extra_info": extra_info
                }
            ]
        }
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters": parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
            logger.error("An error occurred: %s", e, exc_info=True)
            return {"success":False,"result":response[0]}
   
    @Logger.generate
    def export(self, query: str, user_id, chat_id, session) -> str:
        """
        Export the current working file.

        Args:
            query (str): JSON string containing the export name.
            user_id: The ID of the user.
            chat_id: The ID of the chat.
            session: The current session object.

        Returns:
            str: JSON response indicating success or failure with the result of the export operation.
        """
        params = json.loads(query)
        mongo_chats = MongoFactory(mongo_client, "chats", session)
        status_msg, chat = mongo_chats.get_by_id(chat_id)
        cwf=chat.get("cwf", {})
        source_id=cwf.get("source_id")
        user_info = {"user_id": user_id, "chat_id": chat_id}
        intent_name = "export"
        export_name = "document.csv"
        if source_id not in ["", None]:
            source_id = source_id if isinstance(source_id, str) else None
        if params.get("export_name")  not in ["", None]:
            export_name = params.get("export_name","document.csv") if isinstance(params.get("export_name","document.csv"), str) else "document.csv"
        parameters = {"groups": [{"user_id": user_id, "job_id": chat_id}], "source": {"source_id": source_id}, "export_name": export_name}
        data = {
            "user_info": user_info,
            "intent_name": intent_name,
            "parameters" : parameters,
            "type": "execute"
        }
        try:
            response = ExecuteService(session).execute(data) 
            return {"success":True,"result":response[0]}
        except requests.RequestException as e:
           logger.error("An error occurred: %s", e, exc_info=True)
           return {"success":False,"result":response[0]}


    def run(self, mode: str, query: str, user_id, chat_id, session) -> str:
        """
        Execute the specified operation mode with the given query and parameters.

        Args:
            mode (str): The operation mode to execute.
            query (str): JSON string containing the query parameters.
            user_id: The ID of the user.
            chat_id: The ID of the chat.
            session: The current session object.

        Returns:
            str: JSON response indicating success or failure with the result of the operation.
        """
        if mode == "add_columns":
            output = self.add_columns(query, user_id, chat_id, session)
        elif mode == "aggregations":
            output = self.aggregations(query, user_id, chat_id, session)
        elif mode == "arithmetic_operations":
            output = self.arithmetic(query, user_id, chat_id, session)
        elif mode == "cast":
            output = self.cast(query, user_id, chat_id, session)
        elif mode == "concat":
            output = self.concat(query, user_id, chat_id, session)
        elif mode == "correlation":
            output = self.correlation(query, user_id, chat_id, session)
        elif mode == "cwf":
            output = self.current_working_file(query, user_id, chat_id, session)
        elif mode == "date_format":
            output = self.date_format(query, user_id, chat_id, session)
        elif mode == "deduplicate":
            output = self.deduplicate(query, user_id, chat_id, session)
        elif mode == "drop_all_except_columns":
            output = self.drop_all_except_columns(query, user_id, chat_id, session)
        elif mode == "drop_columns":
            output = self.drop_columns(query, user_id, chat_id, session)
        elif mode == "export":
            output = self.export(query, user_id, chat_id, session)
        elif mode == "extract":
            output = self.extract(query, user_id, chat_id, session)
        elif mode == "fill_na":
            output = self.fill_na(query, user_id, chat_id, session)
        elif mode == "filter":
            output = self.filter_data(query, user_id, chat_id, session)
        elif mode == "joins":
            output = self.joins(query, user_id, chat_id, session)
        elif mode == "lowercase":
            output = self.lowercase(query, user_id, chat_id, session)
        elif mode == "rearrange_columns":
            output = self.rearrange_columns(query, user_id, chat_id, session)
        elif mode == "rename_columns":
            output = self.rename_columns(query, user_id, chat_id, session)
        elif mode == "replace_special_characters":
            output = self.replace_special_characters(query, user_id, chat_id, session)
        elif mode == "sort":
            output = self.sort(query, user_id, chat_id, session)
        elif mode == "split":
            output = self.split(query, user_id, chat_id, session)
        elif mode == "sql_operations":
            output = self.sql_operations(query, user_id, chat_id, session)
        elif mode == "trim":
            output = self.trim(query, user_id, chat_id, session)
        elif mode == "union":
            output = self.union(query, user_id, chat_id, session)
        elif mode == "uppercase":
            output = self.uppercase(query, user_id, chat_id, session)
        elif mode == "when_otherwise":
            output = self.when_otherwise(query, user_id, chat_id, session)
        elif mode == "drop_na":
            output = self.drop_na(query, user_id, chat_id, session)
        elif mode == "pytool":
            output = self.pytool(query, user_id, chat_id, session)
      
        else:
            output = f"ModeError: Got unexpected mode {mode}."

        try:
            return json.dumps(output)
        except Exception:
            return str(output)
        