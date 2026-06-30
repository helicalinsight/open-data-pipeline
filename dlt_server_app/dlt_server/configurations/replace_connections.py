from dlt_server.models.connector import MongoConnector
from core.mongo.mongo_factory import MongoFactory
from .prepare_connection_id import PrepareConnectionId
from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *

mongo_connector = MongoConnector()
mongo_client = mongo_connector.client
mongo_schedule = MongoFactory(mongo_client, "schedule")
mongo_connections = MongoFactory(mongo_client, "connections")
prepare_connection_id = PrepareConnectionId()
logger = Logger


class ReplaceConnections:
    @logger.generate
    def get_replace_connections(self,schedule_id):
        try:
            success, chat = mongo_schedule.get_by_id(schedule_id)
            if not success or chat is None:
                logger.debug("Chat history not found.")
                raise Exception
            replace_connections = chat.get('replace_connections', {})
            return replace_connections
        except Exception as e:
            logger.error(f"Error getting replace connections with schedule_id: {schedule_id}")
            raise UtilsException("Failed to get replace_connections.") from e

    def _is_valid_connection_id(self, conn_id):
        success, doc = mongo_connections.get_by_id(conn_id)
        return success and doc is not None

    @logger.generate
    def process(self, connection_id_dict, schedule_id, user_id):
        try:
            replace_connections = self.get_replace_connections(schedule_id)
            if not replace_connections:
                logger.info("No connections to replace.")
            else:
                for old_conn, new_conn in replace_connections.items():
                    if isinstance(new_conn, dict) and "connectionId" in new_conn:
                        new_conn = new_conn["connectionId"]
                    if old_conn in connection_id_dict:
                        conn_type = connection_id_dict[old_conn]["type"]
                        if conn_type == "file":
                            connection_id_dict[old_conn]["details"] = prepare_connection_id.get_file_details_of_user(new_conn, user_id)
                        elif conn_type == "database":
                            connection_id_dict[old_conn]["details"] = prepare_connection_id.get_connection_details(new_conn)
                    else:
                        # Try updating new connection for file and database type. Both functions handle the case where
                        # connection id is invalid
                        if self._is_valid_connection_id(new_conn):
                            connection_id_dict = prepare_connection_id.prepare_conn_for_database(connection_id_dict, new_conn)
                        else:
                            connection_id_dict = prepare_connection_id.prepare_conn_for_file(connection_id_dict, user_id, new_conn)
                        logger.info(f"New connection {new_conn} is added.")
            return connection_id_dict
        except Exception as e:
            logger.error(f"Error occured while processing replace connections: connection_id_dict :{connection_id_dict}, schedule_id :{schedule_id} and user_id :{user_id}")
            raise UtilsException("Failed to process replace connections.") from e
