import os
import random
from pandas import DataFrame
import numpy as np
import pandas as pd

from ....exceptions.exception import *
from ....logger.logger import Logger, logger

class Write:
    """
    This is the class for writing data to the given path.
    This class provides methods to write feather and other internal methods.
    """
    @staticmethod
    @Logger.generate
    def feather(dataframe: DataFrame, file_path: str) -> None:
        """
        Writes a Pandas DataFrame to a Feather file format
        This method allows you to save the DataFrame to a feather file

        :param dataframe: The Pandas DataFrame to be written to the Feather file.
        :type dataframe: pandas.DataFrame
        :param file_path: The path where the Feather file will be saved, including the file name and `.feather` extension.
        :type file_path: str
        :return: A boolean indicating success or failure, The path where the file was saved.
        :rtype: bool, str
        """
        try:
            logger.info("Writing dataframe to feather.")
        
            base, ext = os.path.splitext(file_path)
            path = f"{base}{ext}"
            dataframe.reset_index(inplace=True, drop=True)
            dataframe = convert_mixed_types_to_object(dataframe)
            dataframe.to_feather(file_path)
            dataframe.to_feather(path)
            logger.info("Successfully wrote dataframe to feather.")
            return True, path
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while writing to Feather file: {str(e)}", exc_info=True)
            raise UtilsException("Failed to write the feather file.") from e


def is_binary_data(series):
    return series.apply(lambda x: isinstance(x, bytes)).any()

def convert_mixed_types_to_object(df):
    """
    Converts a DataFrame containing mixed data types to a DataFrame where all values are represented as strings. 
    This method ensures uniformity in data representation by transforming each entry in the DataFrame to its string equivalent, facilitating operations that require consistent data types

    :param dataframe: The Pandas DataFrame whose data types need to be converted to strings
    :type dataframe: pandas.DataFrame
    :return: The DataFrame with all values converted to strings
    :rtype: pandas.DataFrame

    """
    for col in df.columns:
        if df[col].dtype == 'object':
            if is_binary_data(df[col]):
                continue
            types = df[col].apply(type).value_counts()
            if len(types) > 1:
                # Preserve missing values (NaN, NaT, None)
                mask = df[col].isna() | df[col].apply(lambda x: isinstance(x, (pd.NaT.__class__, type(None))))
                
                # Convert only non-null values to 'object'
                df.loc[~mask, col] = df.loc[~mask, col].astype(str).astype(object)
    return df
