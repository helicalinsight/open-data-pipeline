import re

import pandas
import chardet

from ....exceptions.exception import *
from ....logger.logger import Logger, logger
from ....utilities.utilities import ReadUtils

read_utils = ReadUtils()

class Read:
    """
    The Read class is designed to handle various file formats and facilitate the reading of data from these formats, specifically CSV, Excel, and Feather. This class provides a set of methods tailored for reading data from:

    CSV Files: Load data from .csv files.
    Excel Files: Read data from .xlsx files (Excel spreadsheets).
    Feather Files: Import data from Feather files.
    """
    @staticmethod
    @Logger.generate
    def csv(path, settings=None, catalog={}):
        """
        Reads a CSV file using the Pandas library, allowing for efficient data manipulation and analysis. 
        The method imports the data from the specified file path and optionally limits the number of rows read if specified in the settings

        :param path: The path of the CSV file to be read.
        :type path: str
        :param settings: A dictionary containing settings such as the total number of records to be read, defaults to none
        :type settings: dict, optional
        :return: The status of the read operation (True if successful) and the dataframe.
        :rtype: bool, pandas.DataFrame
        """
        try:
            logger.info("Reading csv file.")
            num_rows = settings.get('files', {}).get('num_records', None) if settings else None
            columns = []
            if catalog != {}:
                file_id, columns = catalog.popitem()
            with open(path, 'rb') as f:
                result = chardet.detect(f.read())
                file_encoding = result['encoding'] if result['encoding'] else 'ISO-8859-1'
            if num_rows is not None and num_rows != -1:
                if len(columns) > 0:
                    dataframe = pandas.read_csv(path, encoding=file_encoding, nrows=num_rows,usecols=columns)
                else:
                    dataframe = pandas.read_csv(path, encoding=file_encoding, nrows=num_rows, on_bad_lines='skip')
            else:
                if len(columns) > 0:
                    dataframe = pandas.read_csv(path, encoding=file_encoding,usecols=columns)
                else:
                    dataframe = pandas.read_csv(path, encoding=file_encoding)
            dataframe.columns = read_utils.map_columns(dataframe)
            dataframe[dataframe.select_dtypes(include=['object']).columns] = dataframe.select_dtypes(include=['object']).apply(lambda col: col.astype(str).where(~col.isna(), col))
            logger.info("Successfully read csv file.")
            return True, dataframe
        except Exception as e:
            logger.error(f"An error occurred while reading csv file: {str(e)}", exc_info=True)
            raise UtilsException("Failed to read the csv file.") from e

    @staticmethod
    @Logger.generate
    def xlsx(path, settings=None, catalog={}):
        """
        Reads a Excel file using the Pandas library, allowing for efficient data manipulation and analysis. 
        The method imports the data from the specified file path and optionally limits the number of rows read if specified in the settings


        :param path: The path of the Excel file to be read.
        :type path: str
        :param settings: A dictionary containing settings such as the total number of records to be read, defaults to none
        :type settings: dict, optional
        :return: The status of the read operation (True if successful) and the dataframe.
        :rtype: bool, pandas.DataFrame
        """
        try:
            logger.info("Reading excel file.")
            num_rows = settings['files'].get('num_records', None) if settings else None
            sheet_name = None
            columns = []
            if catalog != {}:
                sheet_name, columns = catalog.popitem()
                sheet_name = sheet_name.split(".")[-1]
            # sheet_name = catalog.get("title")# catalog is a dict key is sheet name value is columns to load
            if num_rows is not None and num_rows != -1:
                if sheet_name:
                    if len(columns) > 0:
                        dataframe = pandas.read_excel(path, nrows=num_rows, sheet_name=sheet_name, usecols=columns)
                    else:
                        dataframe = pandas.read_excel(path, nrows=num_rows, sheet_name=sheet_name)
                else:
                    dataframe = pandas.read_excel(path, nrows=num_rows)
            else:
                if sheet_name:
                    if len(columns) > 0:
                        dataframe = pandas.read_excel(path, sheet_name=sheet_name, usecols=columns)
                    else:
                        dataframe = pandas.read_excel(path, sheet_name=sheet_name)
                else:
                    dataframe = pandas.read_excel(path)
            dataframe.columns = read_utils.map_columns(dataframe)
            dataframe[dataframe.select_dtypes(include=['object']).columns] = dataframe.select_dtypes(include=['object']).apply(lambda col: col.astype(str).where(~col.isna(), col))
            logger.info("Successfully read excel file.")
            return True, dataframe
        except Exception as e:
            logger.error(f"An error occurred while reading xlsx file: {str(e)}", exc_info=True)
            raise UtilsException("Failed to read the excel file.") from e


    @staticmethod
    @Logger.generate
    def xls(path, settings=None, catalog={}):
        """
        Reads a Excel file using the Pandas library, allowing for efficient data manipulation and analysis. 
        The method imports the data from the specified file path and optionally limits the number of rows read if specified in the settings


        :param path: The path of the Excel file to be read with .xls extension.
        :type path: str
        :param settings: A dictionary containing settings such as the total number of records to be read, defaults to none
        :type settings: dict, optional
        :return: The status of the read operation (True if successful) and the dataframe.
        :rtype: bool, pandas.DataFrame
        """
        try:
            # sheet_name = catalog.get("title")
            sheet_name, columns = catalog.popitem()
            if catalog != {} and len(catalog) != 0:
                status,dataframe=Read.xlsx(path, settings=None, sheet_name=sheet_name, usecols=columns)
            else:
                status,dataframe=Read.xlsx(path, settings=None)
            return status, dataframe
        except Exception as e:
            raise UtilsException("Failed to read the excel file.") from e
        
    @staticmethod
    @Logger.generate
    def feather(path):
        """
        Reads a feather file using the Pandas library, allowing for efficient data manipulation and analysis. 
        The method imports the data from the specified file path


        :param path: The path of the Feather file to be read.
        :type path: str
        :return: The status of the read operation (True if successful) and the dataframe.
        :rtype: bool, pandas.DataFrame
        """
        try:
            logger.info("Reading feather file.")
            dataframe = pandas.read_feather(path)
            logger.info("Successfully read fether file.")
            return True, dataframe
        except Exception as e: # pragma: no cover
           logger.error(f"An error occurred while reading feather file: {str(e)}", exc_info=True)
           raise UtilsException("Failed to read the feather file.") from e
