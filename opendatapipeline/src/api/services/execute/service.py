
from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ....logger.logger import Logger, logger
from ....configurations.api.config import Config



class ExecuteService:
	"""Service for executing operations and handling previews.

    :param session: An optional handle to the session used for database operations.
    :type session: type, optional
    """
	def __init__(self,session=None):
		"""Constructor method

        :param session: An optional handle to the session used for database operations.
        :type session: type, optional
        """
		self.session=session
		self.mongo_connector = MongoConnector()
		self.mongo_client = self.mongo_connector.client
		self.chat_collection = MongoFactory(self.mongo_client, "chats", session=self.session)
		self.config = Config.config

	#TODO:refactor undo redo related function
	@Logger.generate
	def execute(self, req_data):
		"""Executes an operation based on the provided request data.

		This method handles different intents such as 'joins', 'union', and 'export'.
		It manages the corresponding operation and updates the chat collection. If an
		error occurs, it logs the error and aborts the transaction.

		:param req_data: A dictionary containing request data. The expected structure is:
						- 'user_info': A dictionary with user details, including 'chat_id'.
						- 'intent_name': A string specifying the intent of the operation (e.g., 'joins', 'union', 'export').
						- 'parameters': A dictionary with parameters relevant to the intent.
		:type req_data: dict
		:return: A dictionary containing the success status, message, and other relevant
				information. If the operation fails, it returns an error message.
		:rtype: dict
		:raises Exception: If the intent is not recognized or if an operation fails.
		"""
		try:
			from ....etl.transfrom.manager import Manager
			manager = Manager(self.session)
			user_info=req_data.get("user_info", None)
			intent_name = req_data.get("intent_name", None)
			parameters=req_data.get("parameters", None)
			if intent_name in ["export"]:
				result,id,export_name= manager.manage_export(user_info, intent_name, parameters)
				if result:
					self.chat_collection.update_one(user_info.get("chat_id"), "next", []) # this is written to block redo after performing llm operation
					return {"success": True, "text": "File Ready To Download","source_id":id,"export_name":export_name}, 200
			else:
				status, metadata_status,load,msg, details=manager.manage_operation(user_info,intent_name,parameters)
				if status:
					self.chat_collection.update_one(user_info.get("chat_id"), "next", [])
					return {"success":True,"text":msg,"metadata_status":metadata_status,"load":load},200
				else:# pragma: no cover
					raise Exception(msg)
		except Exception as e: # pragma: no cover
			logger.error(f"{e}", exc_info=True)
			try:
				self.session.abort_transaction()
			except Exception as mongoexception:
				pass
			return {"success": False, "text": f"{e}"}, 500

	@Logger.generate
	def preview(self, req_data):
		"""Performs a preview operation based on the provided request data.

		This method handles preview operations by retrieving and returning preview information.
		If an error occurs, it logs the error and aborts the transaction.

		:param req_data: A dictionary containing preview request data. The expected structure is:
						- 'preview_info': A list of dictionaries, where each dictionary contains:
						- 'source_id': The identifier for the source to be previewed.
						- 'alias': An alias or identifier used for the preview.
		:type req_data: dict
		:return: A dictionary containing the success status and preview information. If the preview
				operation fails, it returns an error message.
		:rtype: dict
		:raises Exception: If the preview operation fails.
		"""
		try:
			from ....etl.transfrom.manager import Manager
			manager = Manager(session=self.session)
			preview_info = req_data.get("preview_info", None)
			id = preview_info[0]["source_id"]
			alias = preview_info[0]["alias"]
			user_info = req_data.get("user_info", {})
			chat_id = user_info.get("chat_id")
			_, chat_doc = self.chat_collection.get_by_id(chat_id)
			mode = req_data.get("mode", chat_doc.get("job_mode", "llm"))
			if mode == "yaml":
				response = manager.yaml_preview(chat_id)
			else:
				response = manager.preview(id, alias, chat_id)
			page = int(req_data.get('page')) if req_data.get('page') and int(req_data.get('page')) > 0 else int(self.config["api"]["preview_default_page"])
			per_page = int(req_data.get('per_page')) if req_data.get('per_page') and int(req_data.get('per_page')) > 0 and int(req_data.get('per_page')) < int(self.config["api"]["preview_max_per_page_limit"]) else int(self.config["api"]["preview_default_per_page"])
			if len(response) > 0:
				offset = (page - 1) * per_page
				from_pos = min(offset, len(response[0]["data"]))
				to_pos = min(offset + per_page, len(response[0]["data"]))
				response[0]["data"] = response[0]["data"][from_pos:to_pos]
			else:
				response = [{
					"data": [],
					"total_records": 0
				}]
			if response is not None:
				logger.info("Successfully performed preview")
				return {"success":True,"preview":response, "page":page, "per_page":per_page, "total_records":response[0]["total_records"]},200
			else:# pragma: no cover
				logger.error("Failed to preview", exc_info=True)
				raise Exception(f"Failed to preview with req_data: {req_data}")
				# return {"success": False, "text": "Failed to preview"},500
		except Exception as e: # pragma: no cover
			logger.error(f"{e}", exc_info=True)
			self.session.abort_transaction()
			return {"success": False, "message": f"{e}"}, 500





