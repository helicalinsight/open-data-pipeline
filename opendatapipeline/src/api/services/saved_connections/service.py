from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ....logger.logger import Logger, logger
from src.api.services.base.service_parent import ServiceParent


class SavedConnectionsService(ServiceParent):
    """Service for managing and retrieving saved database connections.

    This service provides functionality to fetch saved connections for a given user, filtered by connection type.

    Attributes:
        session (Session): The database session used for operations.

    Methods:
        get_saved_connections(user_id, type):
            Retrieves saved connections for a specific user and connection type.
    """
    def __init__(self, session=None):
        """Initializes the SavedConnectionsService with a database session.

        Args:
            session (Session): The database session to use for operations.
        """
        self.session = session
        super().__init__(session)

        
    @Logger.generate
    def get_saved_connections(self, user_id,type):
        """Fetches saved connections for the specified user and connection type.

        Args:
            user_id (str): The ID of the user whose connections are to be fetched.
            type (str): The type of connections to retrieve.

        Returns:
            dict: A dictionary containing the success status, a list of connection details, and a message.
                - success (bool): Indicates whether the operation was successful.
                - databases (list or None): A list of connection details if connections are found, otherwise None.
                - msg (str): A message indicating the result of the operation.
            int: HTTP status code representing the result of the operation.

        Raises:
            Exception: If an error occurs during the operation, an error message is logged and a failure response is returned.
        """
        try:

            mongo_connections = MongoFactory(self.client, "connections", session=self.session)

            status, connections = mongo_connections.get_all_by_user_id_key_value(
                user_id, "type", type
            )

            if connections:
                response = [
                    {"_id": str(conn.get("_id")), "alias": conn.get("connection_alias"),
                     "type": type}
                    for conn in connections
                ]
                logger.info("Fetched connections successfully.")
                return {"success": True, "databases": response, "msg": "Fetched connections successfully."}, 200
            else:
                logger.info("No connections found.")
                return {"success": True, "databases": None, "msg": "No connections found."}, 200

        except Exception as e: # pragma: no cover
            logger.error(f"Error fetching connections: {e}", exc_info=True)
            return {"success": False, "msg": "Failed to fetch connections."}, 500