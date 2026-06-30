import yaml
import re
from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
from ..pipeline.utilities import Utilities
logger = Logger
utils = Utilities()


class Read:

    @logger.generate
    def yml(self, path):
        try:
            with open(path, "r") as config_file:
                config = yaml.safe_load(config_file)
            logger.debug(f"yml file path: {path}")
            logger.info("Read the yml file successfully.")
            return config
        except Exception as e:
            logger.error(f"An unexpected error occurred while reading yml: {str(e)}")
            raise UtilsException(f"Failed to read the file.") from e

    @logger.generate
    def csv(self, spark, path, columns=[], config={}):
        """
        Reads a CSV file using Spark

        :param spark: The Spark session to use for reading the CSV file
        :param path: The file path of the CSV file to read
        :return: A DataFrame containing the data read from the CSV file
        """
        try:
            config_dict = {'header': True, 'inferSchema': True}
            config_dict.update(config)
            if len(columns)>0:
                dataframe = spark.read.options(**config_dict).csv(path).select(columns)
            else:
                dataframe = spark.read.options(**config_dict).csv(path)
            new_columns = [utils.clean_column_name(col) for col in dataframe.columns]
            dataframe = dataframe.toDF(*new_columns)
            logger.debug(f"csv file path: {path}")
            logger.info("Read the csv file successfully.")
            return dataframe
        except Exception as e:
            logger.error(f"An unexpected error occurred while reading CSV file: {str(e)}")
            raise UtilsException(f"Failed to read the csv") from e

    @logger.generate
    def xlsx(self, spark, path, columns=[], config={}):
        """
        Reads a XLSX file using Spark

        :param spark: The Spark session to use for reading the Excel file
        :param path: The file path of the Excel file to read
        :return: A DataFrame containing the data read from the Excel file
        """
        try:
            config_dict = {'header': True, 'inferSchema': True}
            config_dict.update(config)
            reader = spark.read.format("com.crealytics.spark.excel")
            for key, value in config_dict.items():
                reader = reader.option(key, value)
            if len(columns)>0:
                dataframe = reader.load(path).select(columns)
            else:
                dataframe = reader.load(path)
            new_columns = [utils.clean_column_name(col) for col in dataframe.columns]
            dataframe = dataframe.toDF(*new_columns)
            logger.debug(f"excel file path: {path}")
            logger.info("Read the excel file successfully.")
            return dataframe
        except Exception as e:
            logger.error(f"An unexpected error occurred while reading Excel file: {str(e)}")
            raise UtilsException(f"Failed to read the excel file.") from e
