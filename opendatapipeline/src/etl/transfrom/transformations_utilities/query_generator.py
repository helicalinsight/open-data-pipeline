
from abc import ABC, abstractmethod
from typing import Union

from ....exceptions.exception import *
from ....logger.logger import Logger, logger

class QueryGenerator(ABC):
    """
    This is the base class for generating query which gets overridden based on filter operation that is being performed
    This class provides methods for generating query based on different filter transformations 
    such as Equals, NotEquals, Contains, NotContains, StartsWith, NotStartsWith, EndsWith, NotEndsWith, 
    IsNull, IsNotNull, IsOneOfThe, IsNotOneOfThe, InRange, InRange, NotInRange, NotInRange, IsGreaterThan, IsGreaterThanOrEqualTo, IslesserThan, IslesserThanOrEqualTo, IsTrue, IsFalse

    """
    @abstractmethod
    def execute(self, columns: Union[str, list], value: Union[str, list]) -> str:
        pass # pragma: no cover


class Equals(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'equals' condition

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            query = f"{column}=={value}"
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for equals: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class NotEquals(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'not equals' condition
        
        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            query = f"{column}!={value}"
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for not equals: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class Contains(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'contains' condition.

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            if isinstance(value[0], str) and len(value) == 1:
                query = f"{column}.str.contains('{value[0]}', na=False)"
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for contains: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class NotContains(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'not contains' condition.
        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            if isinstance(value[0], str) and len(value) == 1:
                query = f"~{column}.str.contains('{value[0]}', na=False)"
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for not_contains: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class StartsWith(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'startswith' condition

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            if isinstance(value[0], str) and len(value) == 1:
                query = f"{column}.str.startswith('{value[0]}', na=False)"
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for startswith: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class EndsWith(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'endswith' condition.

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            if isinstance(value[0], str) and len(value) == 1:
                query = f"{column}.str.endswith('{value[0]}', na=False)"
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for endswith: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class NotStartsWith(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'not startswith' condition.

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            if isinstance(value[0], str) and len(value) == 1:
                query = f"~{column}.str.startswith('{value[0]}', na=False)"
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for not startswith: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class NotEndsWith(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'not endswith' condition.
        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            if isinstance(value[0], str) and len(value) == 1:
                query = f"~{column}.str.endswith('{value[0]}', na=False)"
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for not endswith: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class IsNull(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'is null' condition.

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            query = f"{column}.isnull()"
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is null: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class IsNotNull(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'is not null' condition

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            query = f"{column}.notnull()"
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is not null: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class IsOneOfThe(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'is one of the' condition

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            if isinstance(value, list):
                query = f"{column}.isin({value})"
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is one of the: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class IsNotOneOfThe(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'is not one of the' condition

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            if isinstance(value, list):
                query = f"~{column}.isin({value})"
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is one of the: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class InRange(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'in range' condition

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            if len(value) == 2:
                if isinstance(value[0], int):
                    query = f"{value[0]} <= {column} <= {value[1]}"
                    # 369 <=flim_id <=400
                else:
                    query = f"'{value[0]}' <= {column} <= '{value[1]}'"
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for in range: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class NotInRange(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'not in range' condition

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            if len(value) == 2:
                if isinstance(value[0], int):
                    query = f"~({value[0]} <= {column} <= {value[1]})"
                else:
                    query = f"~('{value[0]}' <= {column} <= '{value[1]}')"
                return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for not in range: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class IsGreaterThan(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'is greater than' condition

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            if isinstance(value[0], int) and len(value) == 1:
                query = f"{column} > {value[0]}"
            else:
                query = f"{column} > '{value[0]}'"
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is greater than: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class IsGreaterThanOrEqualTo(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'is greater than or equal to' condition

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            if isinstance(value[0], int) and len(value) == 1:
                query = f"{column} >= {value[0]}"
            else:
                query = f"{column} >= '{value[0]}'"
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is greater than or equal to: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class IslesserThan(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'is lesser than' condition

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            if isinstance(value[0], int) and len(value) == 1:
                query = f"{column} < {value[0]}"
            else:
                query = f"{column} < '{value[0]}'"
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is lesser than: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class IslesserThanOrEqualTo(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'is lesser than or equal to' condition

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            if isinstance(value[0], int) and len(value) == 1:
                query = f"{column} <= {value[0]}"
            else:
                query = f"{column} <= '{value[0]}'"
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is lesser than or equal to: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class IsTrue(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'is true' condition

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            query = f"{column} == {True}"
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is true: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e


class IsFalse(QueryGenerator):
    @Logger.generate
    def execute(self, column, value):
        """
        Generates an SQL query string for the 'is false' condition

        :param column: The column on which the filter has to be performed
        :type column: str
        :param value: The value to be checked in the given column
        :type value: list or str
        :return: query string
        :rtype: str
        """
        try:
            query = f"{column} == {False}"
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"An error occurred while generating query for is false: {str(e)}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e
