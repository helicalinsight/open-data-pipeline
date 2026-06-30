from src.models.connector import MongoConnector
from src.models.mongo.mongo_factory import MongoFactory
from src.models.mongo.mongo_files import MongoFiles
from src.hooks.database_connector import DatabaseConnector
from core.datasource.base import DBConnection
from src.logger.logger import Logger, logger
import pandas as pd
from src.api.services.base.service_parent import ServiceParent


class S3Service(ServiceParent):
    """
    Service class for listing catalogs and columns from s3.

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
                raise ValueError(
                    f"Missing required parameters - db_type: {db_type}, connection_id: {connection_id}"
                )
            
            connection_details = item.get("connection_details")
            try:
                connector: DBConnection = DatabaseConnector.create_object(db_type)
                connection = connector.connect(connection_details,engine=db_type)
            except Exception as e: # pragma: no cover
                logger.error(f"Error creating connector: {e}", exc_info=True)
                raise Exception(f"Failed to connect to the database.") from e

            try:
                metadata = connector.get_metadata(connection_details,engine=db_type,connection=connection)
                logger.info(f"Data catalog fetched successfully from {db_type}.")
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
            self._safe_abort_transaction()  
            return {"success": False, "msg": f"{e}", "dataCatalog": None}, 500
    