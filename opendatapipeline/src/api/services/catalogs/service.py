from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ....models.mongo.mongo_files import MongoFiles
from ....hooks.database_connector import DatabaseConnector
from core.datasource.base import DBConnection
from ....logger.logger import Logger, logger
import pandas as pd
from src.api.services.base.service_parent import ServiceParent


class ListCatalogsService(ServiceParent):
	"""
    Service class for listing catalogs and columns from a database.

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
		self.mongo_connections = MongoFactory(self.client, "connections", session=self.session)
		self.mongo_files = MongoFiles(self.client, "files", session=self.session)

	
	@Logger.generate
	def list_catalogs(self, req_data):
		"""
		Lists the catalogs available in the specified database connection.

		:param req_data: A dictionary containing the details required to fetch the catalogs.
		:type req_data: dict
		:param req_data['type']: The type of the database (e.g., 'mysql', 'postgres').
		:type req_data['type']: str
		:param req_data['connection_id']: The unique identifier for the database connection.
		:type req_data['connection_id']: str
		:param req_data['database']: The name of the database to fetch the catalogs from.
		:type req_data['database']: str
		:return: A tuple containing a dictionary with success status, message, and data catalog, and an HTTP status code.
		:rtype: tuple(dict, int)
		:return: 
			- success (bool): Indicates whether the catalogs were fetched successfully.
			- dataCatalog (list or None): A list of catalogs if available, otherwise None.
			- msg (str): A message providing more information about the result of the request.
		:raises Exception: If there is an error in processing the request.
		"""
		try:
			if not req_data or not isinstance(req_data, dict):
				raise ValueError(f"Invalid request data: {req_data}")
			
			connection_id = req_data.get("connection_id")
			success, item = self.mongo_connections.get_by_id(connection_id)
			if not success or item is None:
				raise ValueError(f"Invalid connection_id: {connection_id}")
			db_type = item.get("type")
			
			if not all([db_type, connection_id]):
				raise ValueError(f"Missing required parameters(db_type and connection_id) in req_data: {req_data}")
			
			connection_details = item.get("connection_details")

			try:
				connector: DBConnection = DatabaseConnector.create_object(db_type)
				connection = connector.connect(connection_details,engine=db_type)
			except Exception as e: # pragma: no cover
				logger.error(f"Error creating connector: {e}", exc_info=True)
				raise Exception(f"Failed to connect to the database.") from e

			try:
				metadata = connector.get_metadata(connection_details,engine=db_type,connection=connection)
				logger.info("Data catalog fetched successfully")
				return {
					"success": True,
					"dataCatalog": metadata if metadata else None,
					"msg": f"Data catalog fetched successfully from {db_type}.",
				}, 200
			except Exception as e: # pragma: no cover
				logger.error(f"Error getting metadata: {e}", exc_info=True)
				raise Exception("There is some issue in fetching metadata") from e
				# raise Exception(f"Failed to retrieve database metadata: {req_data}") from e
				# return {"success": False, "msg": "Failed to retrieve database metadata.", "dataCatalog": None}, 500

		except Exception as e: # pragma: no cover
			logger.error(f"Unexpected error: {e}", exc_info=True)
			# self.session.abort_transaction()
			self._safe_abort_transaction()
			return {"success": False, "msg": f"{e}", "dataCatalog": None}, 500
		

	@Logger.generate
	def list_columns(self, req_data):
		"""
		Lists the columns available in the specified catalog of the database connection.

		:param req_data: A dictionary containing the details required to fetch the columns.
		:type req_data: dict
		:param req_data['connection_id']: The unique identifier for the database connection.
		:type req_data['connection_id']: str
		:param req_data['catalog']: The name of the catalog to fetch the columns from.
		:type req_data['catalog']: str
		:return: A tuple containing a dictionary with success status, message, and columns data, and an HTTP status code.
		:rtype: tuple(dict, int)
		:return: 
			- success (bool): Indicates whether the columns were fetched successfully.
			- columns (list or None): A list of columns if available, otherwise None.
			- msg (str): A message providing more information about the result of the request.
		:raises Exception: If there is an error in processing the request.
		"""
		try:
			if not req_data or not isinstance(req_data, dict):
				logger.error("Invalid request data.", exc_info=True)
				raise Exception(f"Invalid request data: {req_data}")
				# return {"success": False, "msg": "Invalid request data.", "dataCatalog": None}, 400

			id_type = req_data.get("source")
			connection_id = req_data.get("connection_id")
			catalog = req_data.get("catalog", "")
			
			if id_type == "database":
				if not all([connection_id, catalog]):
					logger.error("Missing required parameters.", exc_info=True)
					raise Exception(f"Missing required parameters in req_data: {req_data}")
					# return {"success": False, "msg": "Missing required parameters.", "dataCatalog": None}, 400

				status, connection_document = self.mongo_connections.get_by_id(connection_id)

				if not connection_document:
					logger.error("Invalid connection ID.", exc_info=True)
					raise Exception(f"Invalid connection ID in req_data: {req_data}")
					# return {"success": False, "msg": "Invalid connection ID.", "dataCatalog": None}, 400

				db_type = connection_document.get("type")
				connection_details = connection_document.get("connection_details")

				try:
					logger.info(f"Creating database connector for {db_type}")
					connector = DatabaseConnector.create_object(db_type)
					connection= connector.connect(connection_details,engine=db_type)
				except Exception as e: # pragma: no cover
					logger.error(f"Error creating connector: {e}", exc_info=True)
					raise Exception(f"Failed to connect to the database with req_data: {req_data}") from e
					# return {"success": False, "msg": "Failed to connect to the database.", "dataCatalog": None}, 500
				try:
					logger.info("Fetching database metadata.")
					metadata = connector.get_columns(connection_details, catalog, engine=db_type, connection=connection)
					logger.info("Columns fetched successfully.")
				except Exception as e:  # pragma: no cover
					logger.error(f"Error getting metadata: {e}", exc_info=True)
					raise Exception(f"Failed to retrieve database metadata. {e}") from e
					# return {"success": False, "msg": "Failed to retrieve database metadata.", "dataCatalog": None}, 500
			else:
				logger.info(f"Fetching file with ID {connection_id}")
				succ, file = self.mongo_files.get_by_file_id_only(connection_id)
				if not file:
					logger.error("Invalid file ID.", exc_info=True)
					raise Exception(f"Invalid file ID in req_data: {req_data}")
				file_path = file.get("file_path")
				file_type = file_path.split(".")[-1]
				logger.info(f"Reading file of type {file_type}")
				if file_type =="csv":
					df = pd.read_csv(file_path, nrows=0)
				elif file_type in ["xlsx", "xls"]:
					sheet_name = catalog.split(".")[-1]#frontend sends it like this "msheets.Sheet1"
					if sheet_name:
						df = pd.read_excel(file_path, nrows=0, sheet_name=sheet_name)
					else:
						df = pd.read_excel(file_path, nrows=0)
				metadata = df.columns.to_list()
			
			logger.info(f"Columns fetched successfully from {id_type}.")
			return {
				"success": True,
				"columns": metadata if metadata else None,
				"msg": f"Columns fetched successfully from {id_type}.",
			},200

		except Exception as e: # pragma: no cover
			logger.error(f"Unexpected error: {e}", exc_info=True)
			# self.session.abort_transaction()
			self._safe_abort_transaction()
			return {"success": False, "msg": f"{e}", "columns": []}, 500

