from abc import ABC, abstractmethod
import pandas
from pandas import DataFrame

from typing import Union, List
import logging
import numpy as np
import duckdb



from ..transformations_utilities.utilities import TransformerUtilities
from ..transformations_messages.transformations_messages import Messages
from  ....exceptions.exception import *
from ....logger.logger import Logger, logger
from src.api.services.audit_log.utils import audit_usage_decorator

util = TransformerUtilities()
msg = Messages()


class Transformer(ABC):
    """
    This is the base class for various data transformations, with each transformation being customized based on the intent name. The class includes methods for performing a wide range of transformations, 
    such as add_columns, concat, correlation, date_format, deduplicate, drop_all_columns_except, drop_columns, drop_na, extract, fill_na, filter_value, joins, lower_case, pytool, rearrange_columns, rename_columns, replace_special_characters, 
    sort, split, trim, union, upper_case, when_otherwise, aggregate, typecast, expression, sql
    """
    def __init__(self, intent_name=None, user_info=None):
        self.intent_name = intent_name
        self.user_info = user_info

    @abstractmethod
    def execute(self, dataframe: Union[DataFrame, List[DataFrame]], parameters: Union[dict, None]) -> DataFrame:
        pass # pragma: no cover
    
    @audit_usage_decorator()
    def execute_with_audit(self, dataframe, parameters) -> DataFrame:
        return self.execute(dataframe, parameters)


class AddColumns(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Modifies an existing DataFrame by adding new columns, the specifications of which are determined by the provided parameters

        :param dataframe: The input Pandas DataFrame to which new columns will be added.
        :type dataframe: pandas.DataFrame
        :param parameters: A dictionary where keys are column names to be added, and values are default values for those columns.
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
         The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        logger.info("Adding columns.")
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"AddColumns is not capable of handling this request. More information: {group['extra_info']} {group['default']}")
                columns = group.get("columns")
                default = group.get("default")
                if columns:
                    columns = util.get_distinct_columns(columns, dataframe)
                    if isinstance(default, list):
                        for add_column,value in zip(columns, default):
                            dataframe[add_column] = value
                    else:
                        for add_column in columns:
                            dataframe[add_column] = default
                    success = True
                    metadata = True
                    message = msg.add_columns(parameters, success)
                else:
                    message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            logger.info("Successfully added columns")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error("Operation 'add_columns' completed with exception: %s", exception, exc_info=True)
            raise DataTransformationException(f"Failed to add columns.{exception}") from exception


class RenameColumns(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Renames a specified column in the DataFrame based on the provided parameters

        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups which has old_column and new_column values in it
                            to perform rename columns
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Renaming columns.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"RenameColumns is not capable of handling this request. More information: {group['extra_info']}")
                old_name = group.get("old_name")
                new_name = group.get("new_name")
                new_name = util.get_distinct_columns([new_name], dataframe)[0]
                group['new_name'] = new_name	
                if old_name and new_name:
                    dataframe.rename(columns={old_name: new_name}, inplace=True, errors="raise")
                    success = True
                    metadata = True
                    message = msg.rename_columns(parameters, success)
                else:
                    missing_params = []
                    if not old_name:
                        missing_params.append("'old_name'")
                    if not new_name:
                        missing_params.append("'new_name'")
                    message = f"Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: [{', '.join(missing_params)}]."
            logger.info("Successfully renamed columns.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'rename_columns' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to rename columns.{exception}") from exception


class Sort(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Sorts the DataFrame based on the specified columns

        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups which has column and type of sorting
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Sorting columns.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"Sort is not capable of handling this request. More information: {group['extra_info']}")
                columns = group.get("columns")
                ascending = group.get("ascending", True)
                ascending = True if ascending is None else ascending
                group["ascending"] = ascending
                if columns:
                    for sorting_column in columns:
                        dataframe.sort_values(by=sorting_column, ascending=ascending, inplace=True)
                        dataframe.reset_index(drop=True, inplace=True)
                        success = True
                        metadata = True
                        message = msg.sort(parameters, success)
                else:
                    message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            logger.info("Successfully sorted columns.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'sort' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to sort columns.{exception}") from exception
        
class DropColumns(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Removes the specified columns from the DataFrame

        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups which has list of columns that has to dropped
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Dropping columns.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"DropColumns is not capable of handling this request. More information: {group['extra_info']}")
                columns = group.get("columns")
                if columns:
                    dataframe.drop(columns, axis=1, inplace=True)
                    success, metadata = True, True
                    message = msg.drop_columns(parameters, success)
                else:
                    message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            logger.info("Successfully dropped columns.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'drop_columns' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to drop columns.{exception}") from exception


class DropAllColumnsExcept(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Removes all columns from the DataFrame except for those explicitly listed in the provided parameters

        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups which has list of columns that should not be dropped
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Dropping all columns.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"DropAllColumnsExcept is not capable of handling this request. More information: {group['extra_info']}")
                columns = group.get("columns")
                if columns:
                    columns_to_drop = [column for column in dataframe.columns if
                                       column not in columns]
                    dataframe.drop(columns_to_drop, axis=1, inplace=True, errors="raise")
                    success, metadata = True, True
                    message = msg.drop_all_columns_except(parameters, success)
                else:
                    message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            logger.info("Successfully dropped all columns.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception: # pragma: no cover
            logger.error(f"Operation 'drop_all_columns_except' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to drop all columns.{exception}") from exception

class Deduplicate(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Removes duplicate values from the specified column in the DataFrame

        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups which has list of columns where the duplicates has to be removed
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Deduplicating columns.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"Deduplicate is not capable of handling this request. More information: {group['extra_info']}")
                columns = group.get("columns")
                if columns:
                    dataframe.drop_duplicates(subset=columns, keep='first', inplace=True)
                    success = True
                    metadata = True
                    message = msg.deduplicate(parameters, success)
                else:
                    message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            logger.info("Successfully deduplicated columns.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'deduplicate' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to deduplicate columns.{exception}") from exception


class Split(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Splits the specified column into multiple columns using the provided delimiter and updates the DataFrame with the new columns

        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups which has source column and delimiter
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Splitting columns.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"Split is not capable of handling this request. More information: {group['extra_info']}")
                column = group.get("column")
                delimiter = group.get("delimiter")
                delimiter = " " if not delimiter else delimiter
                group["delimiter"] = delimiter
                if column is not None:
                    splitted_columns_df = dataframe[column].str.split(delimiter, expand=True)
                    unique_columns_df, group = util.get_unique_columns(splitted_columns_df, group, dataframe)
                    dataframe = pandas.concat([dataframe, unique_columns_df], axis=1)
                    success = True
                    metadata = True
                    message = msg.split(parameters, success)
                else:
                    message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."
            logger.info("Successfully splitted columns.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'split' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to split columns.{exception}") from exception


class ReplaceSpecialCharacters(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        This method replaces special characters in a specified column of the given DataFrame
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups which has target_character, source_column and replacement_character
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Replacing special characters.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"ReplaceSpecialCharacters is not capable of handling this request. More information: {group['extra_info']}")
                target_character = group.get("target_character")
                columns = group.get("columns")
                replacement_character = group.get("replacement_character",'')
                if replacement_character is None:
                    replacement_character=''
                group['replacement_character']=replacement_character
                if columns and target_character:
                    pattern = util.get_pattern(target_character)
                    for column in columns:
                        parameters["delimiter"] = dataframe[column].str.contains(pattern).any()
                        # checking if the dataframe values has the given target character
                        dataframe[column] = dataframe[column].str.replace(pattern, replacement_character, regex=True)
                        success = True
                        metadata = True
                        message = msg.replace_special_characters(parameters, success)
                        parameters.pop("delimiter",None)
                else:
                    missing_params = []
                    if not columns:
                        missing_params.append("'columns'")
                    if not target_character:
                        missing_params.append("'target_character'")
                    message = f"Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: [{', '.join(missing_params)}]."
            logger.info("Successfully replaced special characters.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'replace_special_characters' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to replace special characters.{exception}") from exception



class Concat(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        This method concat two columns with the specified separator in the parameters
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups which has source_column, destination_column and a separator
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Concatinating columns.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"Concat is not capable of handling this request. More information: {group['extra_info']}")
                columns = group.get("columns")
                separator = group.get("separator")
                if columns and len(columns) == 2:
                    destination_column = group.get("destination_column")
                    destination_column = f"{columns[0]}_{columns[1]}_concat" if destination_column is None else destination_column
                    destination_column = util.get_distinct_columns([destination_column], dataframe)
                    separator = " " if separator is None else separator
                    group["separator"] = separator
                    group["destination_column"] = destination_column[0]
                    dataframe[destination_column[0]] = dataframe[columns].astype(str).apply(
                        separator.join, axis=1)
                    success, metadata = True, True
                    message = msg.concat(parameters, success)
                else:
                    message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            logger.info("Successfully concatenation columns.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'concat' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to concat columns.{exception}") from exception



class WhenOtherwise(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Executes a SQL query that uses conditional logic to modify and update the DataFrame
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups which query
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Performing when otherwise operation.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"WhenOtherwise is not capable of handling this request. More information: {group['extra_info']}")
                query_val = group.get("query")
                if query_val:
                    
                    new_columns, group = util.get_new_columns(group, dataframe)
                    group['destination_column'] = new_columns
                    if not [col for col in new_columns if col in dataframe.columns]:
                        dataframe=duckdb.query(group.get("query", "")).df()
                    success = True
                    metadata = True
                    message = msg.when_otherwise(parameters, success)
                else:
                    message = f"Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."
            logger.info("Successfully performed when otherwise.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'when otherwise' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to perform when otherwise.{exception}") from exception


class FilterValue(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Filters the DataFrame based on the specified expression in the parameters
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups which has queries
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Performing filter operation.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None and len(parameters.get("groups")) > 1:
                    raise Exception(f"Filter is not capable of handling this request.")
                columns = group.get('columns')
                expr = group.get('expr')
                value = group.get('value')
                # ["is_null", "is_not_null", "is_true", "is_false"]
                if columns and expr:
                    for column in columns:
                        query = util.generate_query(column, expr, value)
                        dataframe = dataframe.query(query)
                        dataframe.reset_index(drop=True, inplace=True)
                    success, metadata, new_df = True, True, True
                    message = msg.filter_value(parameters, success)
                else:
                    missing_params = []
                    if not columns:
                        missing_params.append("'columns'")
                    if not expr:
                        missing_params.append("'expr'")
                    message = f"Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: [{', '.join(missing_params)}]."
            logger.info("Successfully performed filter.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'filter value' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to filter values.{exception}") from exception



class DateFormat(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Modifies the format of the specified date column in the DataFrame, converting it to the desired date format
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups which has date_format and column
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Updating date format.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"DateFormat is not capable of handling this request. More information: {group['extra_info']}")
                date_format = group.get("format")
                columns = group.get("columns")
                if columns and date_format:
                    for column in columns:
                        if dataframe[column].dtype == 'datetime64[ns]':
                            mapped_format = util.generate_custom_date_format(date_format)
                            dataframe[column] = dataframe[column].astype('datetime64[ns]').dt.strftime(
                                mapped_format)
                            success = True
                            metadata=True
                            message = msg.date_format(parameters, success)
                        else:
                            message = f"The column '{column}' provided is not in date format. Please cast it to date type to change the format."
                else:
                    missing_params = []
                    if not columns:
                        missing_params.append("'columns'")
                    if not date_format:
                        missing_params.append("'format'")
                    message = f"Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: [{', '.join(missing_params)}]."
            logger.info("Successfully updated date format.")
            metadata=True
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'date format' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to format the date.{exception}") from exception


class Correlation(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Calculates the correlation value of the given columns and updates the dataframe
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups with columns and new_column (optional)
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("calculating correlation of the columns.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"Correlation is not capable of handling this request. More information: {group['extra_info']}")
                destination_column = group.get("destination_column", "")
                columns = group.get("columns", [])
                if columns and len(columns) == 2:
                    if destination_column is None:
                        new_column = f"{columns[0]}_{columns[1]}_correlation"
                    else:
                        new_column = util.get_distinct_columns([destination_column], dataframe)[0]
                    group['destination_column'] = new_column
                    dataframe[new_column] = dataframe[columns].corr().iloc[0, 1]
                    success, metadata = True, True
                    message = msg.correlation(parameters, success)
                else:
                    message = f"Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            logger.info("Successfully calculated correlation.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'correlation' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to find correlation of columns.{exception}") from exception



class Trim(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Performs a trim operation on the specified column in the DataFrame based on the given details in the parameters
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups with number_of_characters, location and columns
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name": None, "exception_message": None}
        try:
            logger.info("performing trim.")
            if not parameters:
                message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

                pass
            else:
                for group in parameters.get("groups", []):
                    if "extra_info" in group and group["extra_info"] is not None:
                        raise Exception(f"Trim is not capable of handling this request. More information: {group['extra_info']}")
                    number_of_characters = group.get('number_of_characters')
                    location = group.get('location')
                    columns = group.get('columns')
                    location = "left" if location is None else location
                    number_of_characters = 1 if number_of_characters is None else number_of_characters
                    if columns:
                        for column in columns:
                            '''
                            If length of total number of character exceeds the length of the value in 
                            column the column remains unchanged.
                            '''
                            trim_function = (lambda x: str(x)[:number_of_characters]) if location == 'left' \
                                else (lambda x: str(x)[-number_of_characters:]) if location == 'right' else None
                            if trim_function is not None:
                                dataframe[column] = dataframe[column].apply(trim_function)
                        success = True
                        metadata = True
                        group['number_of_characters'] = number_of_characters
                        group['location'] = location
                        message = msg.trim(parameters, success)
                    else:
                        message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            logger.info("Successfully trimmed given columns.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'trim' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to trim.{exception}") from exception


class UpperCase(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Converts all the values in the specified column of the DataFrame to uppercase
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups with columns
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Perform upper case operation.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"UpperCase is not capable of handling this request. More information: {group['extra_info']}")
                columns = group.get("columns")
                if columns:
                    for column in columns:
                        # if given column does not change to lower case in case of not str type it remains unchanged
                        dataframe[column] = dataframe[column].apply(lambda x: str(x).upper() if isinstance(x, str) else x)
                        success = True
                        metadata = True
                        message = msg.upper_case(parameters, success)
                else:
                    message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            logger.info("Successfully updated columns to upper case.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'upper_case' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to perform upper case.{exception}") from exception



class LowerCase(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Converts all the values in the specified column of the DataFrame to lowercase
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups with columns
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Perform lower case operation.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"LowerCase is not capable of handling this request. More information: {group['extra_info']}")
                columns = group.get("columns")
                if columns:
                    for column in columns:
                        # if given column does not change to lower case in case of not str type it remains unchanged
                        dataframe[column] = dataframe[column].apply(lambda x: str(x).lower() if isinstance(x, str) else x)
                        success = True
                        metadata = True
                        message = msg.lower_case(parameters, success)
                else:
                    message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            logger.info("Successfully updated columns to lower case.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'lower case' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to perform lower case.{exception}") from exception


# Redeclared 'Union' defined above without usage  so changing to UnionDf
class UnionDf(Transformer):
    @Logger.generate
    def execute(self, dataframe: List[DataFrame], parameters: Union[dict, None]):
        """
        Performs a union operation on two DataFrames and return the unioned dataframe
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: list[pandas.DataFrame]
        :param parameters: The dictionary of groups with columns(optional)
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Perform union operation.")
            if not parameters:
                pass
            else:
                for group in parameters.get("groups", []):
                    if "extra_info" in group and group["extra_info"] is not None:
                        raise Exception(f"Union is not capable of handling this request. More information: {group['extra_info']}")
                    columns = group.get('columns')
                    if columns:
                        for index, df in enumerate(dataframe):
                            dataframe[index] = df[columns]
            dataframe = pandas.concat(dataframe, ignore_index=True)
            success = True
            metadata = True
            new_df = True
            message = msg.union(parameters, success)
            logger.info("Successfully performed union.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'union' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to perform union.{exception}") from exception



class Joins(Transformer):
    @Logger.generate
    def execute(self, dataframe: List[DataFrame], parameters: Union[dict, None]):
        """
         Performs a join operation on two DataFrames based on the details specified in parameters and return the unioned dataframe
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: list[pandas.DataFrame]
        :param parameters: The dictionary of groups with join_type, left_on, right_on, filenames
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Perform Joins.")
            file_names = parameters.get("file_names", [])
            if file_names and len(file_names) == 2:
                for group in parameters.get("groups", []):
                    if "extra_info" in group and group["extra_info"] is not None:
                        raise Exception(f"Joins is not capable of handling this request. More information: {group['extra_info']}")
                    join_type = group.get("join_type")
                    join_type = "inner" if not join_type else join_type
                    group["join_type"] = join_type
                    left_on = group.get("left_on")
                    right_on = group.get("right_on")
                    if left_on and right_on:
                        dataframe = pandas.merge(dataframe[0], dataframe[1], how=join_type,
                                            left_on=left_on, right_on=right_on,
                                            suffixes=(
                                                f"_{file_names[0]}", f"_{file_names[1]}"))
                        success = True
                        metadata = True
                        new_df = True
                        message = msg.joins(parameters, success)
                    else:
                        missing_params = []
                        if not left_on:
                            missing_params.append("'left_on'")
                        if not right_on:
                            missing_params.append("'right_on'")
                        message = f"Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: [{', '.join(missing_params)}]."
            else:
                message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['file_names']."
            logger.info("Successfully performed joins.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'joins' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to perform joins.{exception}") from exception


class RearrangeColumns(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Rearranges the columns of the DataFrame according to the specified order as specified in the parameters
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups with list of columns
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Rearranging columns.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"RearrangeColumns is not capable of handling this request. More information: {group['extra_info']}")
                columns = group.get("columns", [])
                if columns and len(columns) >= 1:
                    rearrange_params = group.get('columns')
                    rearrange_params = sorted(rearrange_params, key=lambda x: list(x.values())[0])
                    reference_index = 0
                    for i in range(0, len(rearrange_params)):
                        param_column_name = list(rearrange_params[i].keys())[0]
                        param_column_index = rearrange_params[i][param_column_name]
                        total_cols = len(dataframe.columns) - 1
                        current_index = [col for col in dataframe.columns].index(param_column_name)
                        # case for moving column to last position
                        if param_column_index <= -1:
                            new_column_index = total_cols + param_column_index + 1
                        # case for moving column to first position, having one column
                        if param_column_index == 0 and len(rearrange_params)==1:
                            new_column_index = 0
                            reference_index = current_index
                        # case for moving column to first position, having multiple columns
                        if param_column_index == 0 and len(rearrange_params)>1:
                            reference_column = param_column_name
                            reference_index = current_index
                            new_column_index = reference_index
                        # case for last element
                        if reference_index == total_cols and param_column_index > 0:
                            new_column_index = param_column_index + reference_index - 1
                        # case for first element
                        if reference_index == 0 and param_column_index > 0:
                            new_column_index = param_column_index + reference_index
                        # case for middle elements
                        if reference_index != 0 and reference_index < total_cols and param_column_index > 0:
                            new_column_index = param_column_index + reference_index
                        # case for middle elements but after the reference element
                        if reference_index != 0 and reference_index < total_cols and param_column_index > 0 and current_index < reference_index:
                            reference_index = [col for col in dataframe.columns].index(reference_column)
                            new_column_index = param_column_index + reference_index - 1
                        popped_column = dataframe.pop(param_column_name)
                        # Insert the column
                        dataframe.insert(new_column_index, param_column_name, popped_column)
                        metadata, success = True, True
                        message = msg.rearrange_columns(parameters, success)
                else:
                    message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            logger.info("Successfully rearranged columns.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'rearrange columns' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to rearrange columns.{exception}") from exception

"""
Date formats that are tested and working:
"ddd, MMM DD, YYYY HH:MM:SS"
"yy-mm-dd HH:MM:SS"
"yyyy-mm-dd"
"YYYY-mm-DD"
"MMM d, YYYY"
"YYYY/mm/DD"
"DD-mm-YYYY"
"DD.mm.YYYY"
"d MMMM YYYY"
"d mmmm"
"d MMMM"
"y-m-d H:M:S"
"Y-m-D H:M:S"
"ymd"
"""
class Cast(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Changes the data type of the specified column in the DataFrame to the desired data type
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups with list of columns,new data types and old data types(optional)
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"Cast is not capable of handling this request. More information: {group['extra_info']}")
                columns = group.get('columns')
                new_type = group.get('new_type')
                if columns:
                    if new_type in ["date", "timestamp"]:
                        is_unix = "unix" if util.is_unix(columns, dataframe) is True else None
                        old_type = group.get('old_type') if group.get('old_type') else is_unix
                        if old_type:
                            if old_type in ["unix", "epochs"]:
                                for column in columns:
                                    if dataframe[column].apply(lambda x: len(str(x)) > 10).any():
                                        dataframe[column] = pandas.to_datetime(dataframe[column], unit='ns', errors='raise')
                                    else:
                                        dataframe[column] = pandas.to_datetime(dataframe[column], unit='s', errors='raise')
                                success = True
                                metadata= True                               
                                message, group = msg.cast(parameters, success)
                            else:
                                # to get custom date format

                                existing_format = util.generate_custom_date_format(old_type)

                                dataframe[columns] = dataframe[columns].apply(pandas.to_datetime, errors='raise',
                                                                              format=existing_format)
                                success = True
                                metadata= True
                                message, group = msg.cast(parameters, success)

                        else:
                            try:
                                dataframe[columns] = dataframe[columns].apply(pandas.to_datetime, errors='raise', format="mixed")
                                success = True
                                metadata= True
                                message, group = msg.cast(parameters, success)
                            except Exception as exception:
                                message = f"Operation Completed with Exception: {str(exception)}"
                    else:
                        if new_type:
                            if new_type in ["float", "integer"]:
                                dataframe[columns] = dataframe[columns].apply(pandas.to_numeric, errors='raise',downcast=new_type)
                                success = True
                                metadata= True
                                group['new_type'] = {column: str(dtype) for column, dtype in dataframe[columns].dtypes.to_dict().items()}
                                message, group = msg.cast(parameters, success)
                            elif new_type in ["string", "bool", "boolean", 'object']:
                                if new_type in ["bool", "boolean"]:
                                    dataframe[columns] = dataframe[columns].applymap(lambda x: util.bool_mapping.get(str(x).lower(), x))
                                    if not dataframe[columns].applymap(lambda x: isinstance(x, bool)).all().all():
                                        unmapped_values = util.get_unmapped_values(columns, dataframe)
                                        raise ValueError(f"Cannot map values to boolean: {unmapped_values}")
                                else:
                                    dataframe[columns] = dataframe[columns].apply(lambda x: x.astype(new_type))
                                success = True
                                metadata= True
                                group['new_type'] = {column: str(dtype) for column, dtype in dataframe[columns].dtypes.to_dict().items()}
                                message, group = msg.cast(parameters, success)
                            else:
                                if new_type not in ['float', 'integer', 'bool', 'boolean', 'string','object']:
                                    message ="Please provide the casting type from the below list: ['float', 'integer'," \
                                         "'bool', 'boolean', 'string', 'date', 'timestamp','object']"
                        else:
                            message = f"Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['new_type']."
                else:
                    message = f"Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'cast' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to cast columns.{exception}") from exception


class Aggregations(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict) -> DataFrame:
        """
        Performs aggregation operations on the DataFrame, such as sum, mean, or count, based on specified grouping and aggregation criteria
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups with list of columns, group by(optional), aggregation that has to performed, destination columns(optional)
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        metadata = False
        success = False
        new_df = False
        details = {"exception": False, "exception_name": None, "exception_message": None}
        try:
            logger.info("Perform aggregations.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"Aggregations is not capable of handling this request. More information: {group['extra_info']}")
                columns = group.get("columns")
                destination_columns = group.get("destination_columns")
                aggregations = group.get("agg")
                group_by_columns = group.get("group_by")
                agg_funcs = []
                if aggregations:
                    agg_funcs = util.get_aggregate_function(aggregations)
                if len(group_by_columns) > 0:
                    agg_dict = {}
                    if len(columns) > 0 and len(agg_funcs) > 0:
                        for src_col in columns:
                            for agg_func in agg_funcs:
                                unique_id = f"{agg_func}_{src_col}"  # we will add the new name later after training the bot
                                # if new_columns:
                                #     new_name = new_columns.pop(0) if new_columns else unique_id
                                # else:
                                #     new_name = unique_id
                                agg_dict[unique_id] = (src_col, agg_func)
                        dataframe = dataframe.groupby(group_by_columns, as_index=False).agg(**agg_dict).reset_index(
                            drop=True)
                        metadata, success, new_df = True, True, True
                        message = msg.aggregations(parameters, success)
                    else:
                        message = "Either source_column or aggregation function is not present"
                else:
                    if len(columns) > 0 and len(agg_funcs) > 0:
                        for src_col in columns:
                            for agg_func in agg_funcs:
                                dataframe[f"{agg_func}_{src_col}"] = dataframe[src_col].agg(agg_func)
                        metadata, success, new_df = True, True, False
                        message = msg.aggregations(parameters, success)
                    else:
                        message = "Either source_column or aggregation function is not present"
            logger.info("Successfully performed aggregations.")
            return dataframe, success, metadata, message, new_df, details

        except Exception as exception: # pragma: no cover
            logger.error("Operation 'aggregations' completed with exception: %s", exception, exc_info=True)
            raise DataTransformationException(f"Failed to aggregate columns.{exception}") from exception



class Arithmetic(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Performs arithmetic operations on the given dataframe for the specified query
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups with list of columns, value and operation to be performed
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"Arithmetic operations is not capable of handling this request. More information: {group['extra_info']}")
                query = group.get("query")
                destination_column = group.get("destination_column")
                destination_column = util.get_new_column_name(destination_column, dataframe.columns)
                group['destination_column'] = destination_column
                # if column is having date values it has to be of date type.. string format cannot be subtracted
                if query:
                    dataframe[destination_column] = dataframe.eval(query,engine="python")
                    success, metadata = True, True
                    message = msg.arithmetic_operations(parameters, success)
                else:
                    message = f"Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."
            logger.info("Successfully performed arithmetic operations.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error("Operation 'arithmetic' completed with exception: %s", exception, exc_info=True)
            raise DataTransformationException(f"Failed to perform arithmetic.{exception}") from exception


class SqlOperations(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Executes the given sql query and updates the dataframe
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups which query
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Perform sql operations.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"SQLOperations is not capable of handling this request. More information: {group['extra_info']}")
                query = group.get("query")
                if query:
                    dataframe=duckdb.query(query).df()
                    success = True
                    metadata = True
                    new_df = True
                    message = msg.sql_operations(parameters, success)
                else:
                    message = "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."
            logger.info("Successfully performed sql operations.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'sql operations' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to perform sql operations.{exception}") from exception


class DropNa(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Removes any rows from the DataFrame where the specified columns have missing values
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups which has columns list
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Dropping Na.")
            if not parameters:
                dataframe.dropna(inplace=True)
            else:
                for group in parameters.get("groups", []):    
                    if "extra_info" in group and group["extra_info"] is not None:
                        raise Exception(f"DropNa is not capable of handling this request. More information: {group['extra_info']}")
                    subset = group.get("subset", None)
                    dataframe.dropna(subset=subset, inplace=True)
            success = True
            metadata = True
            message = msg.drop_na(parameters, success)
            logger.info("Successfully dropped Na's.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'drop na' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to drop na.{exception}") from exception



class Extract(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Extracts the specified date component (e.g., year, month, day) from the date column in the DataFrame
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups which has column, component to be extracted
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Extracting data.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"Extract is not capable of handling this request. More information: {group['extra_info']}")
                column = group.get("column")
                components = group.get("component")
                if column and components:
                    for component in components:
                        if dataframe[column].dtype == 'datetime64[ns]':
                            # destination_column = group.get("destination_column")
                            destination_column=None
                            destination_column = f"{column}_{component}" if destination_column is None else destination_column
                            destination_column = util.get_distinct_columns([destination_column], dataframe)
                            group["destination_column"] = destination_column[0]
                            destination_column=destination_column[0]
                            if component == 'year':
                                dataframe[destination_column] = dataframe[column].dt.year
                            elif component == 'month':
                                dataframe[destination_column] = dataframe[column].dt.month
                            elif component == 'day':
                                dataframe[destination_column] = dataframe[column].dt.day
                            success = True
                            metadata = True
                            message = msg.extract(parameters, success)
                        else:
                            message = f"The column '{column}' provided is not in date format. Please cast it to date type to change the format."         
                            raise Exception(message)
                else:
                    missing_params = []
                    if not column:
                        missing_params.append("'column'")
                    if not components:
                        missing_params.append("'component'")
                    message = f"Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: [{', '.join(missing_params)}]."
                    raise Exception(message)
            logger.info("Successfully extracted data.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error("Operation 'extract' completed with exception: %s", exception, exc_info=True)
            raise DataTransformationException(f"Failed to extract.{exception}") from exception



class FillNa(Transformer):
    @Logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict):
        """
        Fills NA/NaN values in the DataFrame using the specified value or method, such as forward fill, backward fill, or a given constant
        
        :param dataframe: The input Pandas DataFrame to which the operation has to be performed.
        :type dataframe: pandas.DataFrame
        :param parameters: The dictionary of groups which has column, value, method, axis, limit details
        :type parameters: dict
        :return: The updated DataFrame, A boolean indicating success or failure, A boolean indicating metadata has to be updated or not, 
                 The message, The boolean value indicating if it has to create new dataframe or not, The details of error messages
        :rtype: pandas.DataFrame, bool, bool, str, bool, dict
        """
        success = False
        metadata = False
        new_df = False
        details = {"exception": False, "exception_name":  None, "exception_message": None}
        try:
            logger.info("Filling Na's.")
            for group in parameters.get("groups", []):
                if "extra_info" in group and group["extra_info"] is not None:
                    raise Exception(f"FillNa is not capable of handling this request. More information: {group['extra_info']}")
                column = group.get("column", "")
                value = group.get("value", None)
                method = group.get("method", None)
                axis = group.get("axis", 0)
                limit = group.get("limit", None)
                if column:
                    if value is not None:
                        dataframe[column] = dataframe[column].fillna(value=value, axis=axis)
                        success = True
                        metadata = True
                        message = msg.fill_na(parameters, success)
                    elif method is not None:
                        dataframe[column] = dataframe[column].fillna(method=method, limit=limit)
                        success = True
                        metadata = True
                        message = msg.fill_na(parameters, success)
                    else:
                        missing_params = []
                        if value is None:
                            missing_params.append("'value'")
                        if method is None:
                            missing_params.append("'method'")
                        message = f"Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: [{' or '.join(missing_params)}]."
                else:
                    if value is not None:
                        dataframe = dataframe.fillna(value=value, axis=axis)
                        success = True
                        metadata = True
                        message = msg.fill_na(parameters, success)
                    elif method is not None:
                        dataframe = dataframe.fillna(method=method, limit=limit)
                        success = True
                        metadata = True
                        message = msg.fill_na(parameters, success)
                    else:
                        missing_params = []
                        if value is None:
                            missing_params.append("'value'")
                        if method is None:
                            missing_params.append("'method'")
                        message = f"Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: [{' or '.join(missing_params)}]."
            logger.info("Successfully filled Na's.")
            return dataframe, success, metadata, message, new_df, details
        except Exception as exception:
            logger.error(f"Operation 'fill na' completed with exception: {str(exception)}", exc_info=True)
            raise DataTransformationException(f"Failed to fill na.{exception}") from exception
