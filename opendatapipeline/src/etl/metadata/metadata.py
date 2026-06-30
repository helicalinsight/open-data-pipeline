import inspect
import os
import pandas

from ...exceptions.exception import *
from ...logger.logger import Logger, logger

class Metadata:
    """
    The Metadata class is designed to generate metadata for a given DataFrame. 
    It provides methods to retrieve column names, data types, the number of columns, the number of rows, and to execute the metadata generation process
    and returns a dictionary containing various aspects of the metadata 
    """
    def __init__(self):
        self.file_info_dict = {}
        self.column_info_dict = {}
        self.statistics_dict = {}
        self.data_distribution_dict = {}
        self.categorical_dict = {}
        self.categorical_nominal = []
        self.categorical_ordinal = []
        self.numerical_discrete = []
        self.numerical_continuous = []

    @Logger.generate
    def column_names(self, df):
        """
        Retrieves the column names from the DataFrame, updates the  dictionary

        :param df: The DataFrame from which column names are to be retrieved.
        :type df: pandas.dataframe
        :return: The updated dictionary containing the column information
        :rtype: dict
        """
        try:
            return self.column_info_dict.update({inspect.currentframe().f_code.co_name: df.columns.tolist()})
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while fetching column names: {e}", exc_info=True)
            return self.column_info_dict.update({inspect.currentframe().f_code.co_name: []})

    @Logger.generate
    def datatypes(self, df):
        """
        Retrieves the data types of the DataFrame's columns and updates the dictionary

        :param df: The DataFrame from which the data types of columns are to be retrieved
        :type df: pandas.dataframe
        :return: The updated dictionary containing the data type information
        """
        try:
            return self.column_info_dict.update({inspect.currentframe().f_code.co_name: {col: str(dtype) for col, dtype
                                                                                         in df.dtypes.items()}})
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while fetching data types: {e}", exc_info=True)
            return self.column_info_dict.update({inspect.currentframe().f_code.co_name: {}})

    @Logger.generate
    def num_of_columns(self, df):
        """
        Retrieves the number of columns in the DataFrame and updates the dictionary

        :param df: The DataFrame whose number of columns is to be retrieved
        :type df: pandas.dataframe
        :return: The updated dictionary containing the number of columns information
        :rtype: dict
        """
        try:
            return self.column_info_dict.update({inspect.currentframe().f_code.co_name: len(df.columns)})
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while fetching number of columns: {e}", exc_info=True)
            return self.column_info_dict.update({inspect.currentframe().f_code.co_name: None})

    @Logger.generate
    def num_of_rows(self, df):
        """
        Retrieves the number of rows in the DataFrame and updates the dictionary

        :param df: The DataFrame whose number of rows is to be retrieved
        :type df: pandas.dataframe
        :return: The updated dictionary containing the number of rows information
        :rtype: dict
        """
        try:
            return self.column_info_dict.update({inspect.currentframe().f_code.co_name: len(df)})
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while fetching number of rows: {e}", exc_info=True)
            return self.column_info_dict.update({inspect.currentframe().f_code.co_name: None})

    # def missing_values(self, df):
    #     """
    #     Calculates the number of missing values in each column of the DataFrame and updates the column_info dictionary

    #     :param df: The DataFrame for which missing values are to be calculated
    #     :return: None
    #     """
    #     try:
    #         return self.column_info_dict.update({inspect.currentframe().f_code.co_name: df.isnull().sum().to_dict()})
    #     except Exception as e: # pragma: no cover
    #         logger.error(f"An error occurred while calculating missing values: {e}")
    #         return self.column_info_dict.update({inspect.currentframe().f_code.co_name: {}})

    # def summary_statistics(self, df):
    #     """
    #     Calculates summary statistics for the DataFrame and updates the statistics_dict

    #     :param df: The DataFrame for which summary statistics are to be calculated
    #     :return: None
    #     """
    #     try:
    #         return self.statistics_dict.update({inspect.currentframe().f_code.co_name: df.describe().to_dict()})
    #     except Exception as e: # pragma: no cover
    #         logger.error(f"An error occurred while calculating summary statistics: {e}")
    #         return self.statistics_dict.update({inspect.currentframe().f_code.co_name: {}})

    # def skewness(self, df):
    #     """
    #     Calculates the skewness of each column in the DataFrame and updates the statistics_dict

    #     :param df: The DataFrame for which skewness is to be calculated
    #     :return: None
    #     """
    #     try:
    #         return self.statistics_dict.update({inspect.currentframe().f_code.co_name: df.skew(numeric_only=True)
    #                                            .to_dict()})
    #     except Exception as e: # pragma: no cover
    #         logger.error(f"An error occurred while calculating skewness: {e}")
    #         return self.statistics_dict.update({inspect.currentframe().f_code.co_name: {}})

    # def kurtosis(self, df):
    #     """
    #     Calculates the kurtosis of each column in the DataFrame and updates the statistics_dict

    #     :param df: The DataFrame for which kurtosis is to be calculated
    #     :return: None
    #     """
    #     try:
    #         return self.statistics_dict.update({inspect.currentframe().f_code.co_name: df.kurtosis(numeric_only=True)
    #                                            .to_dict()})
    #     except Exception as e: # pragma: no cover
    #         logger.error(f"An error occurred while calculating kurtosis: {e}")
    #         return self.statistics_dict.update({inspect.currentframe().f_code.co_name: {}})

    # def quantiles(self, df):
    #     """
    #     Calculates the quantiles (25th, 50th, and 75th percentiles) of each column in the DataFrame and updates the
    #     statistics_dict

    #     :param df: The DataFrame for which quantiles are to be calculated
    #     :return: None
    #     """
    #     try:
    #         quantiles = df.quantile([0.25, 0.50, 0.75], numeric_only=True)
    #         quantiles = {str(key): {str(sub_key): value for sub_key, value in sub_dict.items()} for key, sub_dict in
    #                      quantiles.items()}
    #         return self.statistics_dict.update({inspect.currentframe().f_code.co_name: quantiles})
    #     except Exception as e: # pragma: no cover
    #         logger.error(f"An error occurred while calculating quantiles: {e}")
    #         return self.statistics_dict.update({inspect.currentframe().f_code.co_name: {}})

    # def categorized_data(self, df):
    #     """
    #     Categorizes the columns of the DataFrame into different types (nominal, ordinal, continuous, discrete) and
    #     updates the categorical_dict

    #     :param df: The DataFrame to be categorized
    #     :return: None
    #     """
    #     try:
    #         logger.error("Categorize data Datafrane:", df)
    #         for column in df.columns:
    #             logger.error("Categorize data Datafrane Column:", column)
    #             dtype = df[column].dtype
    #             unique_values = df[column].nunique()
    #             total_values = len(df)
    #             if dtype == 'object':
    #                 if unique_values == total_values:
    #                     self.categorical_nominal.append(column)
    #                 else:
    #                     self.categorical_ordinal.append(column)
    #             elif pandas.api.types.is_numeric_dtype(dtype):
    #                 if unique_values / total_values < 0.05:
    #                     self.numerical_discrete.append(column)
    #                 else:
    #                     self.numerical_continuous.append(column)
    #         categorized_data = {
    #             "categorical": {
    #                 "nominal": self.categorical_nominal,
    #                 "ordinal": self.categorical_ordinal
    #             },
    #             "numerical": {
    #                 "continuous": self.numerical_continuous,
    #                 "discrete": self.numerical_discrete,
    #             }
    #         }
    #         return self.categorical_dict.update({inspect.currentframe().f_code.co_name: categorized_data})
    #     except Exception as e: # pragma: no cover
    #         logger.error(f"Error occurred while categorizing data: {e}")
    #         return self.categorical_dict.update({inspect.currentframe().f_code.co_name: {}})

    @Logger.generate
    def execute(self, df):
        """
        This is the main method that runs all the metadata methods previously defined, generating a detailed metadata of the given DataFrame. It returns the metadata results in a dictionary format

        :param df: The DataFrame for which metadata is to be collected
        :type df: pandas.dataframe
        :return: A boolean indicating success or failure, A dictionary containing collected metadata including file information, column information,
            summary statistics, and data classification
        :rtype: bool, dict
        """
        try:
            methods = [method for method in dir(self) if callable(getattr(self, method)) and not method.startswith("__")
                       ]
            methods = [method for method in dir(self) if callable(getattr(self, method)) and not method.startswith("__")
                       ]
            for method_name in methods:
                method = getattr(self, method_name)
                if method_name not in ('execute'):
                    try:
                        method(df)
                    except Exception as e: # pragma: no cover
                        logger.error(f"Error occurred while executing {method_name}: {e}", exc_info=True)
                        raise Exception(str(e))
            return True, {"file_information": self.file_info_dict, "column_information": self.column_info_dict,
                    "statistics": self.statistics_dict,
                    "data_classification": self.categorical_dict}
        except Exception as e: # pragma: no cover
            logger.error(f"Error occurred during metadata execute: {e}", exc_info=True)
            raise MetadataException("Falied to generate metadata.") from e
