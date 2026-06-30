from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase
from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory

from ....configurations.api.config import BaseConfig
from ....exceptions.exceptions import UtilityException
from ....logger.logger import Logger, logger
from src.api.services.base.service_parent import ServiceParent


class PipelineHistoryUtils(ServiceParent):
    """Utility class for handling pipeline history operations.

    This class provides functionality for validating chat data and formatting
    pipeline history and its parameters. It interacts with MongoDB to retrieve
    and process chat and cache information.
    """
    def __init__(self, session=None):
        """Initializes the PipelineHistoryUtils with a session.

        :param session: The database session to use for operations.
        :type session: Session, optional
        """
        super().__init__(session)
        self.mongo_chats = MongoFactory(self.client, "chats", session=self.session)
        self.mongo_connections=MongoFactory(self.client,"connections", session=self.session)


    @Logger.generate
    def _validate_chat(self, chat_id):
        """Validates if the chat with the given ID exists.

        Retrieves the chat document from the database. Raises an exception if
        the chat is not found.

        :param chat_id: The ID of the chat to validate.
        :type chat_id: str
        :return: The chat document if found.
        :rtype: dict
        :raises ValueError: If the chat is not found.
        """
        status, chat=self.mongo_chats.get_by_id(chat_id)
        if not chat:
            return None
        logger.info("Successfully performed validate chat")
        return chat

    @Logger.generate
    def _format_history(self, history, chat_id):
        """Formats the pipeline history for a given chat ID.

        Processes the history items to format parameters and files based on
        the associated chat configuration.

        :param history: The list of history items to format.
        :type history: list
        :param chat_id: The ID of the chat to use for formatting.
        :type chat_id: str
        :return: A dictionary containing the success status and the formatted history.
        :rtype: dict
        :raises UtilityException: If there is an error formatting the history.
        """
        filtered_history = []
        try:
            status, chat=self.mongo_chats.get_by_id(chat_id)
            for item in history:
                formatted_params, formatted_files, database_alias = self._format_parameters(item, chat.get("cwf", {}), chat.get("files"), chat_id, chat.get("user_id"))
                if formatted_params is not None:
                    filtered_item = {
                        "function": item.get("function"),
                        "parameters": formatted_params,
                        "files": formatted_files,
                    }
                    if database_alias is not None:
                        filtered_item['database_alias'] = database_alias
                    filtered_history.append(filtered_item)
            logger.info("Successfully performed format history")
            return {"success": True, "history": filtered_history}
        except Exception as e: # pragma: no cover
            logger.error(f"{e}", exc_info=True)
            raise UtilityException("Unable to format history") from e
            # {"success": False, "history": filtered_history}

    @Logger.generate
    def _format_parameters(self, item, cwf, files, chat_id, user_id):
        """Formats the parameters based on the function type.

        Converts parameters and files associated with a history item into
        a formatted structure based on the function type.

        :param item: The history item containing function and parameters.
        :type item: dict
        :param cwf: Chat workspace configuration to use for formatting.
        :type cwf: dict
        :param files: Files available in the chat.
        :type files: dict
        :return: A tuple containing formatted parameters and formatted files.
        :rtype: tuple
        :raises UtilityException: If there is an error formatting the parameters.
        """
        formatted_params = None
        formatted_files = None
        database_alias = None
        try:
            function = item.get("function")
            parameters = item.get("parameters", {})
            if function == 'read_files':
                file_name = parameters.get("file_name", "na")
                conn_id = parameters.get("file_id", "na")
                database_alias = "flat_files"
                alias_dataframe= item.get("output",{}).get("dataframe_alias",file_name)
                formatted_params = [{"alias": alias_dataframe,"_id":conn_id}]
            elif function == "read_tables":
                file_name = parameters.get("table_name", "na")
                conn_id = parameters.get("connection_id", "na")
                _, conn = self.mongo_connections.get_by_id(conn_id)
                database_alias = conn.get("type") if conn else "na"
                alias_dataframe= item.get("output",{}).get("dataframe_alias",file_name)
                formatted_params = [{"catalog": alias_dataframe,"_id":conn_id}]
            elif function == "read":
                file_name = parameters.get("file_name", "na")
                conn_id = parameters.get("connection_id", "na")
                _, conn = self.mongo_connections.get_by_id(conn_id)
                database_alias = conn.get("type") if conn else "na"
                alias_dataframe= item.get("output",{}).get("dataframe_alias",file_name)
                formatted_params = [{"catalog": alias_dataframe,"_id":conn_id}]
            elif function in ["joins","union"]:
                groups = parameters.get("groups", {})
                extra_info = groups[0].pop("extra_info", "") if groups else ""
                file_names=parameters.get("file_names", "na")
                alias_dataframe=parameters.get("dataframe_aliases",file_names)
                formatted_params = groups
                formatted_files = [{"alias":alias_dataframe}]
            elif function == "delete_files":
                formatted_params = [{"source_id": parameters.get("source_id", "")}]
                formatted_files = []
            else:
                if function=="pytool":
                        groups=[{"code":"Check YML for Code."}]
                        formatted_params = groups
                        formatted_files = [{"alias": ["Not Available for PyTool"]}]
                else:
                    groups = parameters.get("groups")
                    extra_info = groups[0].pop("extra_info", "") if groups else ""
                    alias = None
                    if parameters.get("source_id"):
                        cache: CacheBase = get_cache(session=self.session)
                        cache_item = cache.get_item(parameters.get("source_id"), user_id, chat_id)
                        if cache_item is None:
                            alias = "na"
                        else:
                            file_name = cache_item.get("file_name")
                            alias = parameters.get("dataframe_alias",file_name)
                    elif parameters.get("dataframe_alias"):
                        alias=parameters.get("dataframe_alias")
                    if groups and alias:
                        formatted_params = groups
                        formatted_files = [{"alias": [alias]}]

            logger.info("Successfully performed format parameters")
            return formatted_params, formatted_files, database_alias
        except Exception as e: # pragma: no cover
            logger.error(f"Unable to format parameters: {e}", exc_info=True)
            raise UtilityException("Unable to format parameters") from e
            # return formatted_params, formatted_files
