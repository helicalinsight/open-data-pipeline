import os
from typing import Optional



from ....models.connector import MongoConnector
from ....models.mongo.mongo_files import MongoFiles
from ....etl.extract.file_operations.read import Read
from ....etl.metadata.file_operations.write import Write
from ..transformations.transfromations import *
from ..pytool.pytool import *
from ....models.mongo.mongo_files import MongoFactory
from ...load.data_loads.data_loads import DataLoads
from ..data_summary.data_summary import DataSummary
from ....exceptions.exception import *
from ....logger.logger import Logger, logger



read = Read()
write = Write()
mongo = MongoConnector()

mongo_client = mongo.client

class Processor:
    """
    The Processor class handles data processing for a given intent name and returns a tuple that includes a status indicating whether the process was successful, 
    the updated DataFrame after processing, metadata status, and messages. 
    The class features methods for executing operations, exporting data, previewing results, and 
    includes internal utility functions such as get_feather_path and prepare_file_path

    """
    def __init__(self, session):
        self.session = session
        self.operation_mapping =  {
            "add_columns": AddColumns,
            "concat": Concat,
            "correlation": Correlation,
            "date_format": DateFormat,
            "deduplicate": Deduplicate,
            "drop_all_columns_except": DropAllColumnsExcept,
            "drop_columns": DropColumns,
            "drop_na": DropNa,
            "extract": Extract,
            "fill_na": FillNa,
            "filter_value": FilterValue,
            "joins": Joins,
            "lower_case": LowerCase,
            "pytool": PyTool,
            "rearrange_columns": RearrangeColumns,
            "rename_columns": RenameColumns,
            "replace_special_characters": ReplaceSpecialCharacters,
            "sort": Sort,
            "split": Split,
            "trim": Trim,
            "union": UnionDf,
            "upper_case": UpperCase,
            "when_otherwise": WhenOtherwise,
            "aggregate": Aggregations,
            "typecast": Cast,
            "expression": Arithmetic,
            "sql": SqlOperations
        }

    @Logger.generate
    def execute_operations(self, intent_name: str, parameters: dict, user_info: dict = {}, execution_type: str = "default", dataframe_configuration=None) -> tuple:
        """
        This method executes a specified intent operation based on the given execution type and returns the updated DataFrame after applying the operation

        :param user_info: The details of the user like user_id, chat id
        :type user_info: dict
        :param intent_name: The name of the intent or operation to execute
        :type intent_name: str
        :param parameters: A dictionary containing parameters needed for the operation
        :type parameters: dict
        :param execution_type: The type of execution ("default", "joins_unions", "export", "pytool")
        :type parameters: str
        :return:  A boolean indicating success or failure, metadata_status, df, msg, new_df, details
        :rtype: bool, bool, pandas.dataframe, str, bool, dict
        """
        try:
            logger.info("'execute_operation' called")
            user_id = user_info.get("user_id")
            chat_id = user_info.get("chat_id")
            if execution_type == "default":
                operation_class = self.operation_mapping.get(intent_name)
                if intent_name == "pytool":
                    status, msg, new_ids, data_dict = operation_class().execute(dataframe_configuration, parameters, user_info, self.session)
                    logger.info(f"status, msg, new_ids, data_dict {status, msg, new_ids, data_dict}")
                    metadata_status, df, new_df, details = None, None, None, {}
                    logger.info(f"df {df}")
                    logger.info(f"new_df {new_df}")
                    details["new_ids"] = new_ids
                else:
                    # chats = MongoFactory(mongo_client, "chats", session=self.session)
                    # get_success, chat_document = chats.get_by_id(user_info["chat_id"])
                    success, feather_file_path = self.get_feather_path(parameters["source_id"], user_id, chat_id)
                    feather_success, df = read.feather(feather_file_path)
                    # Execute transformations based on the provided intent name
                    df, status, metadata_status, msg, new_df, details = operation_class(intent_name, user_info).execute_with_audit(df, parameters)
                logger.info(f"Returning updated dataframe {status, metadata_status, df, msg, new_df, details}")
                return status, metadata_status, df, msg, new_df, details

            elif execution_type == "joins_unions":
                # Get the IDs of the Feather files
                feathers = parameters.get("source_id")
                df_list = []
                for id in feathers:
                    success, feather_file_path = self.get_feather_path(id, user_id, chat_id)
                    success, df = read.feather(feather_file_path)
                    df_list.append(df)
                # Read the Feather files into DataFrames
                if df_list:
                    # Execute transformations based on the provided intent name
                    operation_class = self.operation_mapping.get(intent_name)
                    df, status, metadata_status, msg, new_df, details = operation_class().execute(df_list, parameters)
                    logger.info("Returning updated dataframe")
                    return status, metadata_status, df, msg, new_df, details
        except Exception as e:
            logger.error(f"An error occured while executing operations in the function 'execute_operations': {str(e)}", exc_info=True )           
            raise ExecuteException(e) from e
          

    @Logger.generate
    def execute_export(self,user_info, intent_name: str, parameters: dict) -> str:
        """
        This method executes an export operation, sending data to the specified destination in the given format. 
        It handles the process of exporting data, ensuring that it is correctly formatted and transmitted to 
        the desired location and returns the export name and its id

        :param user_info: The details of the user like user_id, chat id
        :type user_info: dict
        :param intent_name: The name of the intent or operation to execute
        :type intent_name: str
        :param parameters: Has source_id associated with the user
        :type parameters: dict
        :return:  A boolean indicating success or failure, The export id, The export name
        :rtype: bool, str, str
        """
        try:
            user_id = user_info.get("user_id")
            chat_id = user_info.get("chat_id")
            logger.info("'execute_export' called.")
            feather_success, feather_file_path = self.get_feather_path(parameters["source"]["source_id"], user_id, chat_id)
            success, df = read.feather(feather_file_path)
            result,id,export_name=DataLoads(session=self.session).export(user_info,df,parameters)
            logger.info("Returning exported id")
            return result,id,export_name
        except Exception as e: # pragma: no cover
            logger.error(f"An error occured while exporting in the function 'execute_export': {str(e)}", exc_info=True) 
            raise ExecuteException("Failed to execute the operation ' execute_export'.") from e

    @Logger.generate
    def preview(self, feather_id: str, alias: str, df: DataFrame=None, user_id: Optional[str]=None, chat_id: Optional[str]=None):
        """
        This method reads a Feather file identified by the provided feather_id and generates a detailed preview of the resulting DataFrame. 
        The preview includes metadata such as column names, the number of rows, and additional information about the DataFrame

        :param feather_id: The ID of the Feather file
        :type feather_id: str
        :param alias: The alias name associated with feather id
        :type alias: str
        :return:  A boolean indicating success or failure, The preview info dictionary
        :rtype: bool, dict
        """
        try:
            logger.info("Preview in processor is called.")
            if df is None:
                if not user_id and not chat_id:
                    logger.warning("[DEPRECATED] Preview function should be called with user_id and chat_id")
                feather_success, feather_file_path = self.get_feather_path(feather_id, user_id, chat_id)
                if feather_file_path is None:
                    return True, []
                # added file path for testing
                #feather_file_path = "D:\\nlp-master\\askondata\hadoop_local\\65365001d9654d9ec1172f87\\.cache\\65cb43f2007a5f38718b9d6f\\be687a30-1329-4639-a606-16f083afa6e6.feather"
                success, df = read.feather(feather_file_path)  
            _, preview_info = DataSummary().file_preview(df,feather_id,alias)
            logger.info("Successfully completed preview in processor")
            return True, preview_info
        except Exception as e: # pragma: no cover
            logger.error(f"An error occured while previewing file in 'preview': {str(e)}", exc_info=True) 
            raise ExecuteException("Failed to preview the file.") from e

    @Logger.generate
    def get_feather_path(self, source_id: str, user_id: str=None, chat_id: str=None) -> str:
        """
        This method retrieves the path of the Feather file associated with the given Feather ID from a cache collection in MongoDB

        :param source_id: The ID of the Feather file
        :type source_id: str
        :return:  A boolean indicating success or failure, The path of the Feather file
        :rtype: bool, str
        """
        try:
            query = {
                "source_id":source_id,
                "user_id":user_id,
                "chat_id":chat_id
            }
            if not user_id and not chat_id:
                query.pop("user_id")
                query.pop("chat_id")
                logger.warning("[DEPRECATED] This function requires user_id and chat_id along with source_id.")
            logger.info("Getting the feather path")
            feather_files = MongoFiles(mongo_client, "cache", session=self.session)
            
            success, feather_files_document = feather_files.filter_one(query)
            if feather_files_document is None:
                return False, None
            logger.info("Returning feather path")
            return True, feather_files_document["feather_file_path"]
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while getting Feather file path in 'get_feather_path' function: {str(e)}", exc_info=True) 
            raise UtilsException("Failed to fetch feather path.") from e

    @staticmethod
    @Logger.generate
    def prepare_file_path(file_path: str) -> str:
        """
        This method constructs the full path of a file by combining a specified base_path with a file_name

        :param file_path: The file path
        :type file_path: str
        :return:  A boolean indicating success or failure, The updated file path
        :rtype: bool, str
        """
        try:
            logger.info("Preparing file path")
            base_path = os.path.abspath(os.path.join(__file__, "../.."))
            file_path = os.path.join(base_path, "hadoop", file_path)
            logger.info("Returning file_path")
            return True, file_path
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while preparing the file path in 'prepare_file_path' function: {str(e)}", exc_info=True) 
            raise UtilsException("Failed to prepare file path.") from e