from spark_server.models.connector import MongoConnector
from core.mongo.mongo_factory import MongoFactory

from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *

mongo_connector = MongoConnector()
mongo_client = mongo_connector.client
mongo_schedule = MongoFactory(mongo_client, "schedule")
mongo_files = MongoFactory(mongo_client, "files")
mongo_connections = MongoFactory(mongo_client, "connections")
logger = Logger


class PrepareConnectionId:
    @logger.generate
    def get_chat_history(self,schedule_id):
        try:
            success, chat = mongo_schedule.get_by_id(schedule_id)
            if not success or chat is None:
                logger.debug("Chat history not found.")
                raise Exception
            history = chat.get('pipeline')
            return history
        except Exception as e:
            logger.error(f"Error getting chat history: Failed to get chat history with schedule_id :{schedule_id}")
            raise UtilsException("Failed to get chat history.") from e

    @logger.generate
    def get_file_details_of_user(self, file_id, user_id):
        try:
            success, result = mongo_files.get_by_user_id(user_id)
            if not success or result is None:
                raise ValueError(f"No files found for user {user_id}")
            files = result.get("files", [])
            file_details = [file for file in files if file['file_id'] == str(file_id)]
            if len(file_details) == 0:
                raise ValueError(f"Target file {file_id} for user {user_id} not found.")

            target_file = file_details[0]
            result_details = {
                'file_name': target_file['full_name'],
                'file_type': target_file['file_type'].split('.')[1],
                'file_path': target_file['file_path'],
                'full_name': target_file['full_name']
            }
            return result_details
        except Exception as e:
            logger.error(f"Error occured while fetching file details for file_id {file_id} of user {user_id}")
            raise UtilsException("Failed to get the file details of the user.") from e
           
    @logger.generate
    def get_connection_details(self, connection_id):
        try:
            success, conn_details = mongo_connections.get_by_id(connection_id)
            if not success or conn_details is None:
                raise ValueError(f"Connection {connection_id} not found")
            connection_type = conn_details['type']
            conn_details['connection_details']['type'] = connection_type
            conn_details.pop('type', None)
            if 'connection_details' in conn_details:
                conn_details['source_name'] = conn_details['connection_details'].get('sourceName', "None")
            return conn_details['connection_details']
        except Exception as e:
            logger.error(f"Error occured while fetching connection details with connection_id: {connection_id}")
            raise UtilsException("Failed to get the connection details.") from e
        
    @logger.generate
    def prepare_conn_for_file(self, connection_dict, user_id, id):
        try:
            conn_details = self.get_file_details_of_user(id, user_id)
            connection_dict.update({id: {"type": "file"}})
            connection_dict[id]["details"] = (conn_details)
            return connection_dict
        except UtilsException:
            logger.info("Connection id not present for file: connnection_dict :{connection_dict}, user_id :{user_id} and id :{id}")
            return connection_dict
    
    @logger.generate
    def prepare_conn_for_database(self, connection_dict, id):
        try:
            conn_details = self.get_connection_details(id)
            connection_dict.update({id: {"type": "database"}})
            connection_dict[id]["details"] = (conn_details)
            return connection_dict
        except UtilsException:
            logger.info("Connection id not present for database:: connection_dict: {connection_dict} and id: {id}")
            return connection_dict
    
    @logger.generate
    def prepare_conn_for_s3(self, connection_dict, id):
        try:
            conn_details = self.get_connection_details(id)
            connection_dict.update({id: {"source_type": "s3"}})
            connection_dict[id]["details"] = (conn_details)
            return connection_dict
        except UtilsException:
            logger.info("Connection id not present for s3:: connection_dict: {connection_dict} and id: {id}")
            return connection_dict
    
    @logger.generate
    def process(self, schedule_id,user_id):
        try:
            chat_history = self.get_chat_history(schedule_id)
            connection_dict = {}
            for step in chat_history:
                if step['function'] == 'read_files':
                    id = step['parameters']['file_id']
                    connection_dict = self.prepare_conn_for_file(connection_dict, user_id, id)
                if step['function'] == 'read_tables' or step['function'] == 'export_table':
                    id = step['parameters']['connection_id']
                    connection_dict.update({id: {"type": "database"}})
                    connection_dict = self.prepare_conn_for_database(connection_dict, id)
                if step['function'] == 'read':
                    id = step['parameters']['connection_id']
                    connection_dict.update({id: {"source_type": "s3"}})
                    connection_dict = self.prepare_conn_for_s3(connection_dict, id)
            return connection_dict
        except Exception as e:
            logger.error(f"Error occured while processing the data with schedule_id: {schedule_id} and user_id :{user_id}")
            raise UtilsException("Failed to process the data.") from e
