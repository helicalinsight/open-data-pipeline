
from pyspark.sql import DataFrame

from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
logger = Logger


class Dataframes:
    def __init__(self):
        self.dataframes_dict = {}
        self.union_df = None

    @logger.generate
    def get(self):
        try:
            return self.dataframes_dict
        except Exception as e:
            logger.error(f"Operation 'get' dataframes dict completed with exception: {str(e)}")
            raise UtilsException("Failed to get the dataframe.") from e

    @logger.generate
    def update(self, dataframes):
        try:
            logger.debug("Updating dataframes..")
            if isinstance(dataframes, dict):
                self.dataframes_dict.update(dataframes)
                logger.debug("Returning dataframe dict..")
                return self.dataframes_dict
            elif isinstance(dataframes, DataFrame):
                self.union_df = dataframes
                self.dataframes_dict.update({'union_df': self.union_df})
                logger.debug("Returning Unioned dataframe..")
                return self.union_df
        except Exception as e:
            logger.error(f"Operation 'update' dataframes completed with exception: {str(e)}")
            raise UtilsException("Failed to update the dataframe.") from e

    @logger.generate
    def update_df(self, union_df, file_id):
        try:
            logger.debug("Updating dataframes..")
            self.union_df = union_df
            self.dataframes_dict.update({file_id: self.union_df})
            logger.debug("Returning Unioned dataframe..")
            return self.union_df
        except Exception as e:
            logger.error(f"Operation 'update' dataframes completed with exception: {str(e)}")
            raise UtilsException("Failed to update the dataframe.") from e

    @logger.generate
    def get_union(self):
        try:
            logger.debug("Returning Unioned dataframe..")
            return self.union_df
        except Exception as e:
            logger.error(f"Operation 'get_union' dataframes completed with exception: {str(e)}")
            raise UtilsException("Failed to get the unioned dataframe.") from e
