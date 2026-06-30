
from ....hooks.database_connector import DatabaseConnector
from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ....logger.logger import Logger, logger
from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase
import os
from flask import  send_file
from ..base.service_parent import ServiceParent
from src.api.services.base.service_parent import ServiceParent

class DownloadService(ServiceParent):
	"""Service for handling file downloads.

    :param session: A handle to the session used for database operations.
    :type session: type
    """
	def __init__(self, session=None) -> None:
		"""Constructor method

        :param session: A handle to the session used for database operations.
        :type session: type
        """
		super().__init__(session)

	@Logger.generate
	def download_file(self, feather_id, chat_id):
		"""Downloads a file based on the provided feather ID.

		This method retrieves the file details from a MongoDB cache and sends
		the file as a response for download. If the file is not found, it
		logs an error and returns a failure response.

		:param feather_id: Identifier for the file to be downloaded.
		:type feather_id: str
		:param chat_id: Chat identifier for the download session.
		:type chat_id: str
		:return: A response object containing the file for download or an
			error message if the file is not found.
		:rtype: flask.Response or dict
		"""
		try:
			mongo_chats = MongoFactory(self.client, "chats", session=self.session)
			cache: CacheBase = get_cache(session=self.session)
			_, chat = mongo_chats.get_by_id(chat_id)
			if chat is None:
				raise ValueError(f"Invalid chat id {chat_id}")
			user_id = chat.get("user_id", None) if chat is not None else None

			feather_cache = cache.get_item(feather_id, user_id, chat_id)
			if feather_cache is None:
				raise ValueError(f"Cache entry not present for source id {feather_id} and chat {chat_id}")
			
			export_path = feather_cache.get("export_path", None)
			export_name = feather_cache.get("export_name", None)

			# Determine correct MIME type based on file extension
			file_extension = os.path.splitext(export_name)[1].lower()
			
			mimetype_map = {
				'.csv': 'text/csv',
				'.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
				'.xls': 'application/vnd.ms-excel'
			}
			
			mimetype = mimetype_map.get(file_extension, 'application/octet-stream')
			
			logger.info(f"Downloading file: {export_name} with mimetype: {mimetype}")

			# Ensure the file exists and is readable
			if not os.path.exists(export_path):
				raise FileNotFoundError(f"Export file not found: {export_path}")


			# For Excel files, ensure binary mode
			if file_extension in ['.xlsx', '.xls']:
				response = send_file(
					os.path.abspath(export_path), 
					download_name=export_name, 
					as_attachment=True,
					mimetype=mimetype
				)
			else:
				# For CSV files, standard text mode
				response = send_file(
					os.path.abspath(export_path), 
					download_name=export_name, 
					as_attachment=True,
					mimetype=mimetype
				)
			
			logger.info("Successfully downloaded the file")
			return response

		except Exception as e:
			logger.error(f"The file not found {e}", exc_info=True)
			return {
				"success": False,
				"text": "The file not found"
			}, 404

