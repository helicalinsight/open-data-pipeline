from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ....models.mongo.mongo_messages import MongoMessages
from ....exceptions.exceptions import UtilityException
from ....logger.logger import Logger, logger
# mongo_connector = MongoConnector()
# mongo_client = mongo_connector.client


class ChatHistoryUtil:
    """
    Utility class for managing and manipulating chat history data.

    :param session: The database session for interacting with MongoDB.
    :type session: object
    """

    def __init__(self, session):
        """
        Constructor method.

        :param session: The database session for interacting with MongoDB.
        :type session: object
        """
        self.session=session
        self.mongo_connector = MongoConnector()
        self.mongo_client = self.mongo_connector.client
        self.mongo_langchain = MongoMessages(self.mongo_client, "langchain", session=self.session)
        self.mongo_chats = MongoFactory(self.mongo_client, "chats", session=self.session)
        
    @Logger.generate
    def _extract_event_text(self, event):
        """
        Extracts text from user or bot events.

        :param event: The event object containing text or data.
        :type event: dict
        :param event['event']: The type of event, can be 'user' or 'bot'.
        :type event['event']: str
        :param event.get('parse_data', {}).get('metadata', {}).get('value', ''): For 'user' events, the text is extracted from this field.
        :type event.get('parse_data', {}).get('metadata', {}).get('value', ''): str
        :param event.get('text', ''): For 'bot' events, the text is extracted from this field.
        :type event.get('text', ''): str
        :param event.get('data', {}).get('custom', {}).get('data', {}).get('text', ''): Additional field for 'bot' events to extract text.
        :type event.get('data', {}).get('custom', {}).get('data', {}).get('text', ''): str
        :return: The extracted text from the event.
        :rtype: str
        """
        logger.info("Successfully extracted event text")
        return (
            event.get("parse_data", {}).get("metadata", {}).get("value", "")
            if event.get("event") == "user"
            else (
                event.get("text", "")
                or event.get("data", {})
                .get("custom", {})
                .get("data", {})
                .get("text", "")
            )
        )

    @Logger.generate
    def _get_columns_list(self, selected_files, metadata):
        """
        Extracts columns from selected files based on metadata.

        :param selected_files: List of selected file information with file IDs.
        :type selected_files: list of dict
        :param selected_files[].get('alias'): The ID of the file.
        :type selected_files[].get('alias'): str
        :param metadata: Metadata containing column information for files.
        :type metadata: dict
        :param metadata[file_id]: Metadata associated with the file ID.
        :type metadata[file_id]: list of dict
        :param metadata[file_id][0].get('columns', []): List of columns associated with the file ID.
        :type metadata[file_id][0].get('columns', []): list
        :return: A tuple containing a success flag and a list of columns.
        :rtype: tuple(bool, list)
        :return: 
            - success (bool): Indicates whether the columns list was successfully retrieved.
            - columns_list (list): A list of columns extracted from the metadata.
        :raises UtilityException: If unable to get the columns list.
        """
        columns_list = []
        try:
            if selected_files:
                for file_info in selected_files:
                    file_id = file_info["alias"]
                    columns = metadata.get(file_id, [{}])[0].get("columns", [])
                    columns_list.extend(columns)
            logger.info("Successfully got the columns list")
            return True, columns_list
        except: # pragma: no cover
            logger.error("Unable to get column list", exc_info=True)
            raise UtilityException("Unable to get column list")

    @Logger.generate
    def _clear_chat_data(self, langchain):
        """
        Clears chat data from the langchain collection.

        :param langchain: The langchain data to be cleared.
        :type langchain: dict
        :param langchain['chat_id']: The ID of the chat associated with the langchain data.
        :type langchain['chat_id']: str
        :param langchain['messages']: List of messages in the langchain data to be cleared.
        :type langchain['messages']: list
        :return: True if successful, else raises an exception.
        :rtype: bool
        :raises UtilityException: If unable to clear chat data.
        """
        try:
            self.mongo_langchain.update_one_by_chat_id(langchain["chat_id"], "messages", [])
            self.mongo_langchain.update_one_by_chat_id(langchain["chat_id"], "chat_memory", [])
            return True
        except Exception as e: # pragma: no cover
           logger.error(f"Unable to clear chat data str(e)", exc_info=True)
           raise UtilityException("Unable to clear chat data") from e

    @Logger.generate
    def _clear_chat_history(self, chat):
        """
        Clears chat history from the chats collection.

        :param chat: The chat object containing history to be cleared.
        :type chat: dict
        :return: True if successful, else raises an exception.
        :rtype: bool
        :raises UtilityException: If unable to clear chat history.
        """
        try:
            chat["history"] = []

            
            self.mongo_chats.update_one(chat["_id"], "history", chat["history"])
            self.mongo_chats.update_one(chat["_id"], "files", [])
            self.mongo_chats.update_one(chat["_id"], "cwf", {})
            self.mongo_chats.update_one(chat["_id"], "next", [])
            logger.info("Successfully cleared the chat history")
            return True
        except Exception as e: # pragma: no cover
            logger.error("Unable to clear chat history", exc_info=True)
            raise UtilityException("Unable to clear chat history") from e
