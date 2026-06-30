from dlt_server.models.connector import MongoConnector
from core.mongo.mongo_factory import MongoFactory
import sqlglot
import yaml
import uuid

from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *

mongo_connector = MongoConnector()
mongo_client = mongo_connector.client
mongo_schedule = MongoFactory(mongo_client, "schedule")
mongo_audit_runs = MongoFactory(mongo_client, "audit_runs")
mongo_audit_usage = MongoFactory(mongo_client, "audit_usage")
mongo_chat = MongoFactory(mongo_client, "chats")
logger = Logger


class MongoToYamlTranslator:
    @logger.generate
    def get_schedule(self, schedule_id):
        try:
            logger.debug(f"Extracting schedule using schedule id : {schedule_id}")
            success, schedule = mongo_schedule.get_by_id(schedule_id)
            if not success or schedule is None:
                raise UtilsException("Schedule data is not found ")
            return schedule
        except Exception as e:
            logger.error(f"Error getting schedule: {str(e)}")
            raise UtilsException("Schedule not found.") from e

    @logger.generate
    def get_chat_history(self, schedule_id):
        try:
            schedule = self.get_schedule(schedule_id)
            history = schedule.get('pipeline')
            logger.debug("Returning chat history..")
            return history
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            raise UtilsException("Failed to get chat history.") from e
        
    @logger.generate
    def get_code(self, schedule_id):
        try:
            schedule = self.get_schedule(schedule_id)
            code = schedule.get('code')
            logger.debug(f"Code extracted {code}")
            logger.debug("Returning code..")
            return code
        except Exception as e:
            logger.error(f"Error getting code: {str(e)}")
            raise UtilsException("Failed to get code.") from e
        
    @logger.generate
    def filter_for_status_pass(self, chat_history):
        try:
            updated_chat_history = [step for step in chat_history if step.get('status') == 'PASS']
            logger.debug("Returning updated chat history..")
            return updated_chat_history
        except Exception as e:
            logger.error(f"Error filtering chat history for status = PASS: {str(e)}")
            raise UtilsException("Failed to filter the status pass.") from e
    
    @logger.generate
    def update_to_df_id(self, chat_history):
        try:
            for step in chat_history:
                if 'parameters' in step and 'source_id' in step['parameters']:
                    step['parameters']['df_id'] = step['parameters'].pop('source_id')
                if 'output' in step and 'source_id' in step['output']:
                    step['output']['df_id'] = step['output'].pop('source_id')
            return chat_history
        except Exception as e:
            logger.error(f"Error updating source_id to df_id: {str(e)}")
            raise UtilsException("Failed to update to df_id.") from e
    
    @logger.generate
    def convert_duckdb_to_sparksql(self, duckdb_query):
        try:
            sparksql_query = sqlglot.transpile(duckdb_query, read="duckdb", write="spark")[0]
            logger.debug("Returning updated sparksql_query.")
            return sparksql_query
        except Exception as e:
            logger.error(f"Error converting query from DuckDB to SparkSQL: {e}")
            raise UtilsException("Failed to convert duckdb to spark sql.") from e
    
    @logger.generate
    def apply_sql_glot(self, chat_history):
        try:
            for step in chat_history:
                if step['function'] == 'when_otherwise' or step['function'] == 'sql':
                    for group in step['parameters']['groups']:
                        if 'query' in group:
                            group['query'] = self.convert_duckdb_to_sparksql(group['query'])
            return chat_history
        except Exception as e:
            logger.error(f"Error applying sql glot: {e}")
            raise UtilsException("Failed to apply sql glot.") from e

    @logger.generate
    def remove_output_null(self, chat_history):
        try:
            for step in chat_history:
                if step.get('output') is None:
                    step.pop('output', None)
            return chat_history
        except Exception as e:
            logger.error(f"Error removing null output: {e}")
            raise UtilsException("Failed to remove output null.") from e

    @logger.generate
    def remove_unnecessary_keys(self, chat_history):
        try:
            for step in chat_history:
                step.pop('id', None)
                step.pop('step', None)
                step.pop('status', None)
            return chat_history
        except Exception as e:
            logger.error(f"Error removing null output: {e}")
            raise UtilsException("Failed to remove unnecessary keys.") from e

    @logger.generate
    def convert_to_yaml(self, chat):
        try:
            yaml_data = yaml.dump(chat)
            return yaml_data
        except Exception as e:
            logger.error(f"Error converting to YAML: {e}")
            raise UtilsException("Failed to convert to yaml.") from e
    
    @logger.generate
    def process(self,schedule_id):
        try:
            chat_history = self.get_chat_history(schedule_id)
            #chat_history = self.filter_for_status_pass(chat_history)
            chat_history = self.remove_output_null(chat_history)
            chat_history = self.update_to_df_id(chat_history)
            updated_chat_history = self.apply_sql_glot(chat_history)
            updated_chat_history = self.remove_unnecessary_keys(updated_chat_history)
            yml = self.convert_to_yaml(updated_chat_history)
            
            return yml
        except Exception as e:
            logger.error(f"Failed to process the file: {str(e)}")
            raise ProcessorException("Failed to process the data.") from e
    
    @logger.generate
    def get_schedule_document(self, schedule_id):
        '''
        Returns the schedule document from db
        '''
        try:
            success, schedule = mongo_schedule.get_by_id(schedule_id)
            if not success or schedule is None:
                raise UtilsException("Schedule document not found")
            return schedule
        except Exception as e:
            logger.error(f"Error getting schedule for schedule_id {schedule_id}: {str(e)}")
            raise UtilsException("Schedule document not found") from e
        
    @logger.generate
    def get_chat_document(self, chat_id):
        '''
        Returns the chat document from db
        '''
        try:
            success, chat = mongo_chat.get_by_id(chat_id)
            if not success or chat is None:
                raise UtilsException("Chat document not found")
            return chat
        except Exception as e:
            logger.error(f"Error getting chat for chat_id {chat_id}: {str(e)}")
            raise UtilsException("Chat document not found") from e



