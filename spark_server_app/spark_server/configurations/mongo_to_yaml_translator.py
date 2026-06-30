from spark_server.models.connector import MongoConnector
from core.mongo.mongo_factory import MongoFactory
import sqlglot
import uuid
import yaml

from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *

mongo_connector = MongoConnector()
mongo_client = mongo_connector.client
mongo_schedule = MongoFactory(mongo_client, "schedule")
mongo_chat = MongoFactory(mongo_client, "chats")
mongo_audit_runs = MongoFactory(mongo_client, "audit_runs")
mongo_audit_usage = MongoFactory(mongo_client, "audit_usage")
logger = Logger


class MongoToYamlTranslator:
    @logger.generate
    def get_chat(self, schedule_id):
        try:
            success, chat = mongo_schedule.get_by_id(schedule_id)
            if not success or chat is None:
                raise UtilsException("Chat history not found.")
            return chat
        except Exception as e:
            logger.error(f"Error getting chat: {str(e)}")
            raise UtilsException("Chat history not found.") from e

    @logger.generate
    def get_chat_history(self, schedule_id):
        try:
            chat = self.get_chat(schedule_id)
            history = chat.get('pipeline')
            logger.debug("Returning chat history..")
            return history
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            raise UtilsException("Failed to get chat history.") from e
        
    @logger.generate
    def get_code(self, schedule_id):
        try:
            chat = self.get_chat(schedule_id)
            code = chat.get('code')
            logger.debug("Returning code..")
            return code
        except Exception as e:
            logger.error(f"Error getting code: {str(e)}")
            raise UtilsException("Failed to get code.") from e
        
    @logger.generate
    def get_code_from_chat(self, chat_id):
        try:
            chat = self.get_chat_document(chat_id)
            code = chat.get("code")
            return code
        except Exception as e:
            logger.error(f"Error getting code for chat_id {chat_id}: {str(e)}")
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
    def process_chat_pipeline(self, pipeline):
        try:
            chat_history = self.remove_output_null(pipeline)
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


class ExportPipeline:
    """
    Class to handle export pipeline operations.

    Provides methods for exporting pipeline data and preparing schedule data for export.

    Attributes:
        session (Session): The MongoDB session used for transactions.

    Methods:
        export_pipeline(chat_id, user_id, details, chat_document, executionType):
            Exports the pipeline data based on the given parameters and updates the chat history.

        prepare_schedule_data(job_id, user_id, schedule_interval, advanced_scheduling, pipeline, config, schedule_name, code):
            Prepares the schedule data for export based on the given parameters.

    Exceptions:
        UtilityException: If an error occurs during the export process.
    """
    def _get_export_step_history_with_files_list(self, details, export_type):
        if export_type == "localstorage":
            history = {
                "id": str(uuid.uuid4()),
                "step": "export",
                "status": "PASS",
                "function": "export",
                "parameters": details.get("files_list")[0],
                "output":None
            }
        else:
            parameters = {
                "user_id": details["files_list"][0].get("user_id", ""),
                "chat_id": details["files_list"][0].get("chat_id", ""),
                "connection_id": details.get("connection_id", ""),
                "table_name": details.get("catalog", ""),
                "source_id": details["files_list"][0]["source_id"]
            }
            history = {
                "id": str(uuid.uuid4()),
                "step": "export",
                "status": "PASS",
                "function": "export_table",
                "parameters": parameters,
                "output":None
            }
        return history
    
    def _get_export_step_from_last_step(self, chat_history, chat_document, user_id, chat_id):
        if len(chat_history) > 0:
            history = {
                "id": str(uuid.uuid4()),
                "step": "export",
                "status": "PASS",
                "output": None
            }
            last_step = chat_history[-1]
            file_obj = self.get_file_object(
                chat_document.get('files'), last_step.get('parameters'))
            function_name = 'export'
            if last_step.get('function') == 'export':
                data = file_obj
                history["function"] = function_name
                history["parameters"] = data
            elif last_step.get('function') == 'export_table':
                data = last_step.get('parameters')
                data["user_id"] = user_id
                data["chat_id"] = chat_id
                data["source_id"] = file_obj.get("source_id", "")
                function_name = 'export_table'
                history["function"] = function_name
                history["parameters"] = data
            elif last_step.get('function') in ["read_files", "read_tables", "read", "filter_value", "union", "joins", "aggregate", "expression", "sql"]:
                data = self.get_file_object(chat_document.get('files'), last_step.get('output'))
                history["function"] = function_name
                history["parameters"] = data
            elif last_step.get('function') == "pytool":# TODO: Handle the delete case in the pytool.
                if last_step.get('output'): 
                    data = self.get_file_object(chat_document.get('files'), last_step.get('output')[-1])    
                    history["function"] = function_name
                    history["parameters"] = data
                else:
                    history = self._get_export_step_from_last_step(chat_history[:-1], chat_document, user_id, chat_id)
            else:
                data = file_obj
                history["function"] = function_name
                history["parameters"] = data
        else:
            history = {}
        
        if history == {}:
            raise RuntimeError("Unable to determine file to export automatically, please select one")
        return history
    
    @Logger.generate
    def export_pipeline(self, chat_id,user_id, details,chat_document, executionType):# pragma: no cover
        """
        Exports the pipeline data based on the given parameters.

        :param chat_id: The unique identifier for the chat.
        :type chat_id: str
        :param user_id: The unique identifier for the user.
        :type user_id: str
        :param details: The details of the export.
        :type details: dict
        :param chat_document: The document containing chat history.
        :type chat_document: dict
        :param executionType: The type of execution ('pipeline' or other).
        :type executionType: str
        :return: The updated chat history.
        :rtype: list
        :raises UtilityException: If an error occurs during the export process.
        """
        try:
            if executionType == "":
                executionType = "pipeline"
            if executionType == "pipeline" or executionType == "yaml":
                chat_history = chat_document.get("history", [])
                export_type = details.get("type", "localstorage") # If "type" not provided, default to "localstorage"
                
                if "files_list" in details and len(details["files_list"]) > 0:
                    # use the export file supplied in arguments
                    history = self._get_export_step_history_with_files_list(details, export_type)
                else:
                    # determine export file from last step
                    history = self._get_export_step_from_last_step(chat_history, chat_document, user_id, chat_id)
                
                step_export_exist = False
                chat_history = chat_document.get("history", [])
                for i, item in enumerate(chat_history):
                    if item.get("function") in ["export", "export_table"]:
                        chat_history[i] = history
                        step_export_exist = True
                        break
                if step_export_exist:
                    pass
                else:
                    if history:
                        chat_history.append(history)
                    chat_history = chat_document.get("history", [])
                
                return chat_history
            elif executionType == "code":
                logger.info("Export pipeline is not expected to anything for code execution mode")
                return chat_document.get("history", [])
            else:
                raise ValueError("Invalid executionType to export_pipeline")

        except Exception as e:
            logger.error(f"{e}", exc_info=True)
            raise UtilsException(e) from e

    def get_file_object(self, chat_files, parameters):
        for item in chat_files:
            if item.get("alias") == parameters.get("table_name") or item.get("alias") == parameters.get("file_name") or item.get("source_id") == parameters.get("source_id"):
                return item

