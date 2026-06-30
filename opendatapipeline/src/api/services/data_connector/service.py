from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ....logger.logger import Logger, logger
from ....configurations.hooks.config import POOL_SIZE, MAX_OVERFLOW, POOL_TIMEOUT, POOL_RECYCLE
from src.api.services.base.service_parent import ServiceParent

class DataConnectorsService(ServiceParent):
    """
    Service class for managing data connectors, including create, read, update, and delete operations.
    """
    def __init__(self,session=None):
        """
        Initializes the DataConnectorsService with a MongoDB session and connector.

        :param session: The MongoDB session for transactions.
        :type session: pymongo.client_session.ClientSession
        """
        super().__init__(session)
        self.mongo_connections = MongoFactory(self.client, "connections", session=self.session)
    
    @Logger.generate
    def create_data_connector(self, req_data, user_id):
        """
    Creates a new data connector entry in the database.

    :param req_data: The request data containing the details needed to create the data connector.
    :type req_data: dict
    :param req_data['type']: The type of the database connector (e.g., 'mysql', 'postgres', 'snowflake').
    :type req_data['type']: str
    :param req_data['connection_details']: The details required to establish a connection.
    :type req_data['connection_details']: dict
    :param req_data['connection_details']['host']: The hostname or IP address of the database server.
    :type req_data['connection_details']['host']: str
    :param req_data['connection_details']['port']: The port number on which the database server is listening.
    :type req_data['connection_details']['port']: int
    :param req_data['connection_details']['user']: The username for authenticating with the database.
    :type req_data['connection_details']['user']: str
    :param req_data['connection_details']['password']: The password for authenticating with the database.
    :type req_data['connection_details']['password']: str
    :param req_data['connection_details']['database']: The name of the database to connect to.
    :type req_data['connection_details']['database']: str
    :param req_data['connection_details'].get('additional_params'): Optional additional parameters for the connection.
    :type req_data['connection_details'].get('additional_params'): dict, optional
    :param user_id: The user ID associated with the connector.
    :type user_id: str
    :return: A response dictionary containing the success status and a message, along with the connection ID if successful.
    :rtype: tuple
    :return: 
        - success (bool): Indicates whether the data connector was created successfully.
        - connection_id (str): The unique identifier of the newly created data connector, if successful.
        - message (str): A message providing information about the result of the operation.
    :raises Exception: If there is an error in creating the data connector or saving details to the database.
    """
        try:
            if not req_data:
                raise Exception(f"Missing request data: {req_data} with user_id: {user_id}")

            database = req_data.get("connection_details", {}).get("database", None)
            req_data["connection_details"]["database"] = database
            database_type = req_data.get("type")
            connection_details = req_data.get("connection_details")

            req_data["user_id"] = str(user_id)

            
            status, result = self.mongo_connections.insert_document(req_data)

            if result:
                logger.info("Connection saved successfully.")
                return {
                    "success": True,
                    "connection_id": str(result),
                    "message": "Connection saved successfully.",
                }, 200
            else:
                logger.error("Failed to save connection details.", exc_info=True)
                raise Exception(f"Failed to save connection details with req_data: {req_data} and user_id: {user_id}")

        except Exception as e: # pragma: no cover
            logger.error(f"Error saving data connector: {e}", exc_info=True)
            self._safe_abort_transaction()  
            return {
                "success": False,
                "message" : f"{e}"
                # "message": "Error occurred while saving connection.",
            }, 500

    
    @Logger.generate
    def get_all_data_connectors(self, user_id):
        """
        Retrieves all data connectors from the database.

        :return: A response dictionary containing all data connectors details.
        :rtype: tuple
        """
        try:
            _, details = self.mongo_connections.get_all_by_user_id(user_id)
            if details:
                return {
                    "success": True,
                    "data_connectors": [detail for detail in details]
                }, 200
            else:
                return {
                    "success": False,
                    "data_connectors": []
                }, 200
        except Exception as e: # pragma: no cover
            logger.error(f"Error fetching data connectors: {e}", exc_info=True)
            raise Exception(f"Error fetching data connectors: {e}") from e
    
    @Logger.generate
    def get_data_connector(self, connection_id):
        """
        Retrieves the data connector details by its ID.

        :param connection_id: The ID of the connection to retrieve.
        :type connection_id: str
        :return: A response dictionary containing success status and connection data.
        :rtype: tuple
        """
        try:
            

            status, details = self.mongo_connections.get_by_id(connection_id)

            if details:
                db_details = details.get('connection_details', {})
                filtered_data = {
                    'connection_id': str(details['_id']),
                    'connection_details': db_details,
                }
                logger.info("Connection details fetched successfully.")
                return {
                    "success": True,
                    "connection_data": filtered_data,
                    "msg": "Connection details fetched successfully.",
                }, 200

            else:
                logger.error("No connection details found.", exc_info=True)
                raise Exception(f"No connection details found with connection_id: {connection_id}")

        except Exception as e: # pragma: no cover
            logger.error(f"Error fetching connection details: {e}", exc_info=True)
            return {
                "success": False,
                "connection_data": None,
                "msg" : f"{e}"
                # "msg": "Failed to fetch connection details.",
            }, 500

    
    @Logger.generate
    def update_data_connector(self, req_data):
        """
        Updates the data connector details by its ID.

        :param req_data: The request data containing the updated details and connection ID.
        :type req_data: dict
        :param req_data['connection_id']: The unique identifier of the data connector to be updated.
        :type req_data['connection_id']: str
        :param req_data['type']: The updated type of the database connector (e.g., 'mysql', 'postgres', 'snowflake').
        :type req_data['type']: str, optional
        :param req_data['connection_details']: Updated details required to establish a connection.
        :type req_data['connection_details']: dict, optional
        :param req_data['connection_details']['host']: Updated hostname or IP address of the database server.
        :type req_data['connection_details']['host']: str, optional
        :param req_data['connection_details']['port']: Updated port number on which the database server is listening.
        :type req_data['connection_details']['port']: int, optional
        :param req_data['connection_details']['user']: Updated username for authenticating with the database.
        :type req_data['connection_details']['user']: str, optional
        :param req_data['connection_details']['password']: Updated password for authenticating with the database.
        :type req_data['connection_details']['password']: str, optional
        :param req_data['connection_details']['database']: Updated name of the database to connect to.
        :type req_data['connection_details']['database']: str, optional
        :return: A response dictionary containing success status, updated data, and a message.
        :rtype: tuple
        :return:
            - success (bool): Indicates whether the data connector was updated successfully.
            - updated_data (dict): The updated data that was provided in the request.
            - msg (str): A message providing information about the result of the operation.
        :raises Exception: If there is an error in updating the data connector or saving details to the database.
        """
        try:
            if not req_data or not isinstance(req_data, dict):
                raise Exception(f"Invalid request data: {req_data}")

            connection_id = req_data.get("connection_id", None)
            if not connection_id:
                raise Exception(f"Missing connection ID in req_data: {req_data}")


            updated_req_data = {key: value for key, value in req_data.items() if key != 'connection_id'}

            status, result = self.mongo_connections.update_all(connection_id, updated_req_data)
            logger.info("Connection details updated successfully.")
            if result:
                return {
                    "success": True,
                    "updated_data": req_data,
                    "msg": "Connection details updated successfully.",
                }, 200
            else:
                return {
                    "success": True,
                    "updated_data": req_data,
                    "msg": "Data already Updated!.",
                }, 200

        except Exception as e: # pragma: no cover
            logger.error(f"Error updating connection: {e}", exc_info=True)
            self._safe_abort_transaction()  
            return {
                "success": False,
                "connection_id": None,
                "updated_data": None,
                "msg" : f"{e}"
                # "msg": "Failed to update connection details.",
            }, 500

    
    @Logger.generate
    def delete_data_connector(self, req_data):
        """
        Deletes a data connector entry by its ID.

        :param req_data: The request data containing the connection ID.
        :type req_data: dict
        :param req_data['_id']: The unique identifier of the data connector to be deleted.
        :type req_data['_id']: str
        :return: A response dictionary containing success status, a message, and the connection ID.
        :rtype: tuple
        :return:
            - success (bool): Indicates whether the data connector was deleted successfully.
            - msg (str): A message providing information about the result of the operation.
            - connection_id (str): The unique identifier of the deleted data connector.
        :raises Exception: If there is an error in deleting the data connector or if the connector does not exist.
        """
        try:
            
            if not req_data or not isinstance(req_data, dict):
                raise Exception(f"Invalid request data: {req_data}")

            connection_id = req_data.get("_id", None)
            if not connection_id:
                raise Exception(f"Missing connection ID in req_data: {req_data}")


            status, connection_exists = self.mongo_connections.get_by_id(connection_id)
            if not connection_exists:
                raise Exception(f"Connection doesn't exist: req_data: {req_data}")

            if self.mongo_connections.delete_all(connection_id):
                logger.info("Connection deleted successfully.")
                return {"success": True, "msg": "Connection deleted successfully.","connection_id":connection_id}, 200
            else:
                logger.error("Failed to delete the connection.", exc_info=True)
                raise Exception(f"Failed to delete the connection with req_data: {req_data}")

        except Exception as e: # pragma: no cover
            logger.error(f"Error deleting connection: {e}", exc_info=True)
            self._safe_abort_transaction()  
            return {"success": False, "msg": f"{e}", "connection_id": None}, 500
