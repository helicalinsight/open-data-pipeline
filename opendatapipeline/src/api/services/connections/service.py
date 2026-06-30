
from ....hooks.database_connector import DatabaseConnector
from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ....logger.logger import Logger, logger
from ....exceptions.exception import DatabaseConnectorException
from src.api.services.base.service_parent import ServiceParent


class ConnectionService(ServiceParent):# pragma: no cover
	"""
    Service class for managing and testing database connections.

    :param session: The database session for interacting with MongoDB.
    :type session: object
    """
	def __init__(self,session=None):
		"""
        Constructor method.

        :param session: The database session for interacting with MongoDB.
        :type session: object
        """
		super().__init__(session)
		self.mongo_connections=MongoFactory(self.client,"connections", session=self.session)
	
	@Logger.generate
	def test_connection(self, req_data, user_id):
		"""
		Tests a database connection based on the provided request data.

		:param req_data: The request data containing details required to test the database connection.
		:type req_data: dict
		:param req_data['details']: The connection details needed to establish a database connection.
		:type req_data['details']: dict
		:param req_data['details']['connection_id']: Optional ID of an existing connection from which details can be retrieved.
		:type req_data['details']['connection_id']: str, optional
		:param req_data['details']['host']: The hostname or IP address of the database server.
		:type req_data['details']['host']: str
		:param req_data['details']['port']: The port number on which the database server is listening.
		:type req_data['details']['port']: int
		:param req_data['details']['user']: The username to authenticate with the database.
		:type req_data['details']['user']: str
		:param req_data['details']['password']: The password to authenticate with the database.
		:type req_data['details']['password']: str
		:param req_data['details']['database']: The name of the database to connect to.
		:type req_data['details']['database']: str
		:param req_data['details']['warehouse']: Optional, specific to Snowflake, the warehouse to use.
		:type req_data['details']['warehouse']: str, optional
		:param req_data['connector']: The type of database connector to use (e.g., 'mysql', 'postgres', 'snowflake').
		:type req_data['connector']: str
		:param user_id: The ID of the user initiating the connection test.
		:type user_id: str
		:return: A tuple containing a dictionary with success status and message, and an HTTP status code.
		:rtype: tuple(dict, int)
		:return: 
			- success (bool): Indicates whether the connection was tested successfully.
			- message (str): A message providing more information about the result of the connection test.
		:raises DatabaseConnectorException: If there is an issue with the database connector.
		:raises Exception: For other general errors.
		"""
		try:
			details = req_data.get("details")


			connector_db = req_data.get("connector")
			connector = DatabaseConnector.create_object(connector_db)
			
			if details.get("connection_id"):
					status,details = self.mongo_connections.get_by_id(details.get("connection_id"))
					details=details.get("connection_details")

			else:
					details = details
			connection= connector.connect(details,engine=connector_db)
			if connector_db=='snowflake':
				warehouse=details.get("warehouse")
				if not warehouse:
							raise DatabaseConnectorException("Please Edit the DataSource and Add Warehouse Details.")
			if connector.test_connection(details,engine=connector_db,connection=connection):
					
					logger.info("Connection tested successfully")
					return {"success": True, "msg": "Connection tested successfully"}, 200
			else:
					logger.error("Failed to connect", exc_info=True)
					raise Exception(f"Failed to connect with req_data: {req_data} and user_id: {user_id}")
					# return {"success": False, "msg": "Failed to connect"}, 400
		except DatabaseConnectorException as e:
			self._safe_abort_transaction()  
			return {"success": False, "message": f"{e}"}, 500
		except Exception as e:
			logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
			self._safe_abort_transaction()  
			return {"success": False, "msg": f"{e}"}, 500

