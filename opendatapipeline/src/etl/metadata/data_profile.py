import inspect
import logging

from ...exceptions.exception import *
from ...logger.logger import Logger, logger

class DataProfile:
    """
    This class is designed for creating a data profile of a given DataFrame, identifying various characteristics of columns, such as those that can be concatenated or contain dates. 
    It provides methods for Columns, Concat, Date Format, Deduplicate, Drop All Columns Except, Drop Columns, Rename Columns, Filter, Replace Special Characters, Sort, Split, Execute

    """

    def __init__(self):
        self.data_profile_dict = {}

    @Logger.generate
    def columns(self, df):
        """
        Retrieves the column names from the DataFrame and updates the internal profile with the list of these columns. 
        This method provides an overview of the columns present in the DataFrame

        :param df: The Pandas DataFrame whose column names are to be retrieved.
        :type df: pd.DataFrame
        :return: The updated dictionary containing the data profile, reflecting the latest information about the columns and their characteristics within the DataFrame. 
        :rtype: dict
        """
        try:
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: df.columns.tolist()})
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while fetching column names: {e}", exc_info=True)
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})

    @Logger.generate
    def concat(self, dataframe):
        """
        Retrieves the columns from the DataFrame that are suitable for concatenation and updates the internal profile with this information. 
        This method identifies and provides details about columns that can be combined, helping in managing and analyzing related data

        :param dataframe: The DataFrame whose concat columns are to be retrieved
        :type dataframe: pandas.DataFrame
        :return: The updated data_profile_dict dictionary 
        :rtype: dict
        """
        try:
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})
        except Exception as e: # pragma: no cover
            logger.error("An error occurred while suggesting concat columns", str(e), exc_info=True)
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})

    @Logger.generate
    def date_format(self, dataframe):
        """
        Retrieves the columns from the DataFrame that contain date and updates the internal profile with this information. 
        This method identifies columns that hold date values, facilitating date-related analysis and transformations

        :param dataframe: The DataFrame whose date format column are to be retrieved
        :type dataframe: pandas.DataFrame
        :return: The updated dictionary containing the data profile, reflecting the latest information about the columns and their characteristics within the DataFrame. 
        :rtype: dict
        """
        date_format_list = []
        try:
            date_patterns = [
                (r"\d{4}[-/]\d{1,2}[-/]\d{2,4}", "%Y-%m-%d"),  # YYYY-MM-DD or YYYY/MM/DD or YYYY-M-DD or YYYY/M/DD
                (r"\d{1,2}[-/]\d{2}[-/]\d{2,4}", "%m-%d-%Y"),  # MM-DD-YYYY or MM/DD/YYYY or M-DD-YYYY or M/DD/YYYY
            ]
            for column in dataframe.columns:
                for pattern, date_format in date_patterns:
                    if dataframe[column].astype(str).str.match(pattern).any():
                        date_format_info = {column: {"format": date_format}}
                        date_format_list.append(date_format_info)
                        break
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: date_format_list})
        except Exception as e: # pragma: no cover
            logger.error("An error occurred while suggesting date format columns", str(e), exc_info=True)
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})

    @Logger.generate
    def deduplicate(self, dataframe):
        """
        Retrieves the columns from the DataFrame that have a high number of duplicate values and updates the internal profile with this information. 
        This method identifies columns where duplicate entries are prevalent, aiding in data cleaning and deduplication processes.
        
        :param dataframe: The DataFrame from which columns with a high number of duplicate values are to be retrieved
        :type dataframe: pandas.DataFrame
        :return: The updated dictionary containing the data profile, reflecting the latest information about the columns and their characteristics within the DataFrame. 
        :rtype: dict
        """
        try:
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})
        except Exception as e: # pragma: no cover
            logger.error("An error occurred while suggesting deduplicate columns", str(e), exc_info=True)
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})

    @Logger.generate
    def drop_all_columns_except(self, dataframe):
        """
        Retrieves the columns from the DataFrame that should be retained and updates the internal profile with this information

        :param dataframe: The DataFrame whose drop columns are to be retrieved
        :type dataframe: pandas.DataFrame
        :return: The updated dictionary containing the data profile, reflecting the latest information about the columns and their characteristics within the DataFrame. 
        :rtype: dict
        """
        try:
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})
        except Exception as e: # pragma: no cover
            logger.error("An error occurred while suggesting drop columns", str(e), exc_info=True)
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})

    @Logger.generate
    def drop_columns(self, dataframe):
        """
        Retrieves the columns from the DataFrame that should be dropped and updates the internal profile with this information

        :param dataframe: The DataFrame whose drop columns are to be retrieved
        :type dataframe: pandas.DataFrame
        :return: The updated dictionary containing the data profile, reflecting the latest information about the columns and their characteristics within the DataFrame. 
        :rtype: dict
        """
        try:
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})
        except Exception as e: # pragma: no cover
            logger.error("An error occurred while suggesting drop columns", str(e), exc_info=True)
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})

    @Logger.generate
    def filter(self, dataframe):
        """
        Retrieves the columns from the DataFrame that are suitable for filtering and updates the internal profile with this information

        :param dataframe: The DataFrame whose filter columns are to be retrieved
        :type dataframe: pandas.DataFrame
        :return: The updated dictionary containing the data profile, reflecting the latest information about the columns and their characteristics within the DataFrame. 
        :rtype: dict
        """
        try:
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})
        except Exception as e: # pragma: no cover
            logger.error("An error occurred while suggesting filter columns", str(e), exc_info=True)
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})

    @Logger.generate
    def rename_columns(self, dataframe):
        """
        Retrieves the columns from the DataFrame that are suitable for renaming and updates the internal profile with this information

        :param dataframe: The DataFrame whose rename columns are to be retrieved
        :type dataframe: pandas.DataFrame
        :return: The updated dictionary containing the data profile, reflecting the latest information about the columns and their characteristics within the DataFrame. 
        :rtype: dict
        """
        try:
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})
        except Exception as e: # pragma: no cover
            logger.error("An error occurred while suggesting rename columns", str(e), exc_info=True)
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})

    @Logger.generate
    def replace_special_characters(self, dataframe):
        """
        Retrieves the columns from the DataFrame where special characters are present and updates the internal profile with this information, indicating where character replacement is needed

        :param dataframe: The DataFrame whose replace_special_characters columns are to be retrieved
        :type dataframe: pandas.DataFrame
        :return: The updated dictionary containing the data profile, reflecting the latest information about the columns and their characteristics within the DataFrame. 
        :rtype: dict
        """
        try:
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})
        except Exception as e: # pragma: no cover
            logger.error("An error occurred while suggesting replace_special_characters columns", str(e), exc_info=True)
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})

    @Logger.generate
    def sort(self, dataframe):
        """
        Retrieves the columns from the DataFrame that are suitable for sorting and updates the internal profile with these columns, indicating which ones can be used for ordering operations

        :param dataframe: The DataFrame whose sort columns are to be retrieved
        :type dataframe: pandas.DataFrame
        :return: The updated dictionary containing the data profile, reflecting the latest information about the columns and their characteristics within the DataFrame. 
        :rtype: dict
        """
        try:
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})
        except Exception as e: # pragma: no cover
            logger.error("An error occurred while suggesting sort columns", str(e), exc_info=True)
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})

    @Logger.generate
    def split(self, dataframe):
        """
        Identifies columns in the DataFrame that can be split based on the presence of a delimiter and updates the internal profile with these columns

        :param dataframe: The DataFrame whose split column are to be retrieved
        :type dataframe: pandas.DataFrame
        :return: The updated dictionary containing the data profile, reflecting the latest information about the columns and their characteristics within the DataFrame. 
        :rtype: dict
        """
        try:
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})
        except Exception as e: # pragma: no cover
            logger.error("An error occurred while suggesting split columns", str(e), exc_info=True)
            return self.data_profile_dict.update({inspect.currentframe().f_code.co_name: []})

    @Logger.generate
    def execute(self, df):
        """
        This is the main method that runs all the data profiling methods previously defined, generating a detailed profile of the given DataFrame. It returns the profiling results in a dictionary format

        :param df: The DataFrame for which metadata is to be collected
        :type df: pandas.DataFrame
        :param file_name: The name of the file associated with the DataFrame
        :type file_name: str
        :return: A dictionary containing collected metadata including file information, column information,
            summary statistics, and data classification
        :rtype: bool, dict
        """
        try:
            logger.info("Generating data profile.")
            methods = [method for method in dir(self) if callable(getattr(self, method)) and not method.startswith("__")
                       ]
            for method_name in methods:
                method = getattr(self, method_name)
                if method_name != 'execute':
                    method(df)
            logger.info("Returning generated data profile dict.")
            return True, self.data_profile_dict
        except Exception as e: # pragma: no cover
            logger.error(f"Error occurred during data profile execute: {e}", exc_info=True)
            raise MetadataException("Failed to generate data profile.") from e
