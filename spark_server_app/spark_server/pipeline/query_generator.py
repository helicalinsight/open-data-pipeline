
from abc import ABC, abstractmethod
from typing import Union
from pyspark.sql.functions import col

from ..exceptions.exceptions import *
from ..logger.logger import Logger, logger
logger = Logger

class QueryGenerator(ABC):
    @abstractmethod
    def execute(self, columns: Union[str, list], value: Union[str, list]) -> str:
        pass # pragma: no cover


class Equals(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for equals
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            # in spark list cannot be directly compared to a column
            if isinstance(value, str):
                query = f"{column} = '{value}'"
            elif isinstance(value, (int, bool, float)):  # Handle integer values
                query = f"{column} = {value}"
            elif isinstance(value, list):
                # Convert list values to string and join them with comma
                value_str = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) for v in value])
                query = f"{column} IN ({value_str})"
            #query = col(column) in value if isinstance(value, list) else col(column) == value
            logger.info(f"Generated query for equals: {query}")
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for equals: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class NotEquals(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for not equals
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            if isinstance(value, str):
                query = f"{column} != '{value}'"
            elif isinstance(value, (int, bool, float)):  # Handle integer values
                query = f"{column} != {value}"
            elif isinstance(value, list):
                # Convert list values to string and join them with comma
                value_str = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) for v in value])
                query = f"{column} NOT IN ({value_str})"
            #query = ~col(column) in value if isinstance(value, list) else col(column) != value
            logger.info(f"Generated query for not equals: {query}")
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for not equals: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class Contains(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for contains
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            if isinstance(value[0], str) and len(value) == 1:
                query = col(column).contains(value[0])
                logger.info(f"Generated query for contains: {query}")
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for contains: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class NotContains(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for not contains
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            if isinstance(value[0], str) and len(value) == 1:
                query = ~col(column).contains(value[0])
                logger.info(f"Generated query for not contains: {query}") 
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for not_contains: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class StartsWith(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for startswith
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            if isinstance(value[0], str) and len(value) == 1:
                query = col(column).startswith(value[0])
                logger.info(f"Generated query for startswith: {query}")
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for startswith: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class EndsWith(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for endswith
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            if isinstance(value[0], str) and len(value) == 1:
                query = col(column).endswith(value[0])
                logger.info(f"Generated query for endswith: {query}")
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for endswith: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class NotStartsWith(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for not startswith
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            if isinstance(value[0], str) and len(value) == 1:
                query = ~col(column).startswith(value[0])
                logger.info(f"Generated query for not startswith: {query}")
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for not startswith: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class NotEndsWith(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for not endswith
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            if isinstance(value[0], str) and len(value) == 1:
                query = ~col(column).endswith(value[0])
                logger.info(f"Generated query for not endswith: {query}")
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for not endswith: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class IsNull(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for is null
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            query = col(column).isNull()
            logger.info(f"Generated query for isnull: {query}")
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is null: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class IsNotNull(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for is not null
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            query = col(column).isNotNull()
            logger.info(f"Generated query for is notnull: {query}")
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is not null: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class IsOneOfThe(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for is one of the
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            if isinstance(value, list):               
                query = col(column).isin(value)
                logger.info(f"Generated query for isoneofthe: {query}")
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is one of the: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class IsNotOneOfThe(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for is not one of the
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            if isinstance(value, list):
                query = ~col(column).isin(value)
                logger.info(f"Generated query for isnotoneofthe: {query}")
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is one of the: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class InRange(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for in range
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            if len(value) == 2:
                if isinstance(value[0], int):
                    query = f"{value[0]} <= {column} AND {column} <= {value[1]}"
                    # 369 <=flim_id <=400
                else:
                    query = f"'{value[0]}' <= {column} AND {column} <= '{value[1]}'"
                logger.info(f"Generated query for in range: {query}")
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for in range: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class NotInRange(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for not in range
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            if len(value) == 2:
                if isinstance(value[0], int):
                    query = f"({column} < {value[0]} OR {column} > {value[1]})"
                    # 369 <=flim_id <=400
                else:
                    query = f"({column} < '{value[0]}' OR {column} > '{value[1]}')"
                logger.info(f"Generated query for not inrange: {query}")
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for not in range: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class IsGreaterThan(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for is greater than
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            if isinstance(value[0], int) and len(value) == 1:
                query = f"{column} > {value[0]}"
            else:
                query = f"{column} > '{value[0]}'"
            logger.info(f"Generated query for is greater than: {query}")
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is greater than: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class IsGreaterThanOrEqualTo(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for is greater than or equal to
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            if isinstance(value[0], int) and len(value) == 1:
                query = f"{column} >= {value[0]}"
            else:
                query = f"{column} >= '{value[0]}'"
            logger.info(f"Generated query for is greater than or equal to: {query}")
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is greater than or equal to: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class IslesserThan(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for is lesser than
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            if isinstance(value[0], int) and len(value) == 1:
                query = f"{column} < {value[0]}"
            else:
                query = f"{column} < '{value[0]}'"
            logger.info(f"Generated query for is lesser than: {query}")
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is lesser than: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class IslesserThanOrEqualTo(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for is lesser than or equal to
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            if isinstance(value[0], int) and len(value) == 1:
                query = f"{column} <= {value[0]}"
            else:
                query = f"{column} <= '{value[0]}'"
            logger.info(f"Generated query for is lesser than or equal to: {query}")
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is lesser than or equal to: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class IsTrue(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for is true
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            query = col(column) == True
            logger.info(f"Generated query for is true: {query}")
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is true: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e


class IsFalse(QueryGenerator):
    @logger.generate
    def execute(self, column, value):
        """
        Generates sql query string for is false
        :param column: The column on which the filter has to be performed
        :param value: The value to be checked in the given column
        :return: query string
        """
        try:
            query = col(column) == False
            logger.info(f"Generated query for is false: {query}")
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is false: {str(e)}")
            raise UtilsException(f"Failed to generate query.") from e
