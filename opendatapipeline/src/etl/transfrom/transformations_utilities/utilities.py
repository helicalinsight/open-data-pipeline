
import re

from .query_generator import *
from ....exceptions.exception import *
from ....logger.logger import Logger

class TransformerUtilities:
    """
    This class provides utility methods used for various transformations. 
    It includes functions for generating patterns, creating unique column names, 
    and checking Unix timestamps, get_unmapped_values, get distinct columns, generate custom date format,
    generating column and datatype dictionary, generating query for filter operations
    and get aggregate functions

    """
    def __init__(self) -> None:
        self.mappings = {
            "is not": "!=",
            "is not equal to": "!=",
            "greater than": ">",
            "is greater than": ">",
            "less than": "<",
            "is less than": "<",
            "greater than or equal to": ">=",
            "is greater than or equal to": ">=",
            "less than or equal to": "<=",
            "is less than or equal to": "<=",
            "is equal to": "==",
            "equal to": "=="
        }
        self.common_mapping = {
            # years
            'YYYY': '%Y', 'yyyy': '%Y', 'Y': '%Y', 'YY': '%Y',
            'yy': '%y', 'y': '%y',  # two digit year

            # months
            'mm': '%m', 'm': '%m',

            # names of months
            'mmm': '%b', 'MMM': '%b',

            # full month name
            'mmmm': '%B', 'MMMM': '%B',

            # days
            'dd': '%d', 'd': '%d', 'DD': '%d', 'DD,': '%d,', 'd,': '%d,', 'D': '%d',

            # week days
            'ddd,': '%a,', 'dddd': '%A',

            # hours
            'H': '%H', 'HH': '%H', 'hh': '%I', 'h': '%I',

            # minutes
            'MM': '%M', 'M': '%M',

            # seconds
            'SS': '%S', 'ss': '%S', 'S': '%S',

            # AM/PM
            'AP': '%p', 'ap': '%p'
        }
        self.query_mapping = {
            'equals': Equals(),
            'not_equals': NotEquals(),
            'contains': Contains(),
            'not_contains': NotContains(),
            'startswith': StartsWith(),
            'not_startswith': NotStartsWith(),
            'endswith': EndsWith(),
            'not_endswith': NotEndsWith(),
            'is_null': IsNull(),
            'is_not_null': IsNotNull(),
            'is_one_of_the': IsOneOfThe(),
            'is_not_one_of_the': IsNotOneOfThe(),
            'in_range': InRange(),
            'in_between': InRange(),
            'not_in_range': NotInRange(),
            'not_in_between': NotInRange(),
            'is_greater_than': IsGreaterThan(),
            'is_greater_than_or_equal_to': IsGreaterThanOrEqualTo(),
            'is_lesser_than': IslesserThan(),
            'is_lesser_than_or_equal_to': IslesserThanOrEqualTo(),
            'is_true': IsTrue(),
            'is_false': IsFalse()
        }

        self.bool_mapping = {'true': True,  '1': True, 1: True,
                             'false': False, '0': False, 0: False}

    @Logger.generate
    def get_pattern(self, target_character):
        """
        This method generates a regular expression (regex) pattern for a specified character. 
        It constructs a pattern that accurately represents the provided character in regex format

        :param target_character: The column on which the filter has to be performed. If None, a default pattern is used.
        :type target_character: str
        :return: The compiled regex pattern.
        :rtype: re.Pattern
        """
        try:
            if target_character is not None:
                pattern = re.compile(fr'[{re.escape("".join(target_character))}]+')
            else:
                pattern = re.compile(r'[\s\W]+')
            return pattern
        except Exception as e:		    
            logger.error(f"An error occured: Failed to get the pattern with target_character: {target_character}", exc_info=True)
            raise UtilsException("Failed to get the pattern.") from e

    @Logger.generate
    def get_new_column_name(self, destination_column, column_list):
        """
        This method generates a unique column name by considering the provided destination column name and the list of existing column names. It ensures that the new column name does not conflict with any of the names already present in the dataset

        :param destination_column: The desired name for the new column. If None, a default name is generated.
        :type destination_column: str
        :param column_list: A list of existing column names in the DataFrame.
        :type column_list: list
        :return: A unique column name that does not exist in the column_list.
        :rtype: str
        """
        try:
            if destination_column is None:
                i = 1
                while f"new_column_{i}" in column_list:
                    i += 1
                destination_column = f"new_column_{i}"
            else:
                if destination_column in column_list:
                    i = 1
                    while f"{destination_column}_{i}" in column_list:
                        i += 1
                    destination_column = f"{destination_column}_{i}"
            return destination_column
        except Exception as e:
            logger.error(f"An error occured: Failed to get new column names with destination_column: {destination_column} and column_list: {column_list}", exc_info=True)
            raise UtilsException("Failed to get new column names.") from e

    @Logger.generate
    def is_unix(self, columns, dataframe):
        """
        Determines whether the specified columns in the given DataFrame contain Unix timestamps and return bool

        :param columns: A list of column names to be checked in the DataFrame.
        :type columns: list
        :param dataframe: The Pandas DataFrame containing the data.
        :type dataframe: pandas.DataFrame
        :return: True if any of the specified columns contain Unix timestamps, False otherwise.
        :rtype: bool
        """
        try:
            unix_pattern = r'^-?\d+(\.\d{1,3})?$'
            if dataframe[columns].apply(lambda x: x.astype(str).str.match(unix_pattern).any()).any():
                return True
            return False
        except Exception as e:
            logger.error(f"Operation 'check_unix' executed with exception: Failed to check unix with columns: {columns} and dataframe: {dataframe}", exc_info=True)
            raise UtilsException("Failed to check unix.") from e

    @Logger.generate
    def get_unmapped_values(self, columns, dataframe):
        """
        Identifies unmapped values in the specified columns of the DataFrame and returns 

        :param columns: A list of column names to be checked in the DataFrame.
        :type columns: list
        :param dataframe: The Pandas DataFrame containing the data.
        :type dataframe: pandas.DataFrame
        :return: A string describing the unmapped values for each column.
        :rtype: str
        """
        try:
            unmapped_values = {}
            for col in columns:
                unmapped_values[col] = dataframe[~dataframe[col].isin([True, False])][col].tolist()
            unmapped_values = [f"{col} contains {list(set(values))}" for col, values in unmapped_values.items()]
            unmapped_values_text = ', '.join(unmapped_values)
            return unmapped_values_text
        except Exception as e:
            logger.error(f"Operation 'get_unmapped_values' executed with exception: Failed to get unmapped values with columns: {columns} and dataframe: {dataframe}", exc_info=True)
            raise UtilsException("Failed to get unmapped values.") from e


    @Logger.generate
    def get_distinct_columns(self, columns, dataframe):
        """
        Ensures that the provided column names are unique within the DataFrame by appending a suffix if necessary.

        :param columns: A list of column names to be checked and modified if necessary.
        :type columns: list
        :param dataframe: The Pandas DataFrame containing the existing columns.
        :type dataframe: pandas.DataFrame
        :return: A list of unique column names.
        :rtype: list
        """
        try:
            for i, column in enumerate(columns):
                new_column_name = column
                suffix = 1
                while new_column_name in dataframe.columns:
                    new_column_name = f"{column}_{suffix}"
                    suffix += 1
                columns[i] = new_column_name
            return columns
        except Exception as e:
            logger.error(f"Operation 'get_unique_destination_columns' executed with exception: Failed to get distinct columns with columns: {columns} and dataframe: {dataframe}", exc_info=True)
            raise UtilsException("Failed to get distinct columns.") from e

    @Logger.generate
    def get_new_columns(self, group, dask_df):
        """
        This method identifies potential new column names from a SQL query and generates unique names for them to ensure there is no duplication within the provided DataFrame. The method analyzes the SQL query to extract column names and then generates unique names that do not conflict with existing column names in the DataFrame
        :param group: A dictionary containing the query and other relevant details.
        :type group: dict
        :param dask_df: The DataFrame containing the existing columns.
        :type dask_df: DataFrame
        :return: The new columns,  and the updated query in group
        :rtype: list, dict
        """
        try:
            select_clause = group["query"].split('SELECT ')[1].split('FROM')[0]
            new_columns = []
            if "__newcolumn__" in group["query"]:
                i = 1
                while f"new_column_{i}" in dask_df.columns:
                    i += 1
                while "__newcolumn__" in group["query"]:
                    group["query"] = group["query"].replace("__newcolumn__", f"new_column_{i}", 1)
                    new_columns.append(f"new_column_{i}")
                    i += 1
            else:
                # Extract aliases using regular expression
                new_column_pattern = r'\s+AS\s+(\w+)\s+'
                new_columns = re.findall(new_column_pattern, group["query"], re.IGNORECASE)
                if len(new_columns) > 0:
                    alias_pattern = re.compile(r'\bAS\s+{}\b'.format(new_columns[0]), re.IGNORECASE)
                    new_columns = self.get_distinct_columns(new_columns, dask_df)
                    group["query"] = alias_pattern.sub(f'AS {new_columns[0]}', group["query"], count=1)
            return new_columns, group
        except Exception as e:
            logger.error(f"An error occured: Failed to get new columns with group: {group} and dask_df: {dask_df}", exc_info=True)
            raise UtilsException("Failed to get new columns.") from e

    @Logger.generate
    def get_unique_columns(self, splitted_columns_df, group, dataframe):
        """
        This method ensures that the column names in the split DataFrame are unique when compared to the columns in the original DataFrame. It modifies the column names of the split DataFrame to avoid conflicts and maintain uniqueness within the context of the original DataFrame

        :param splitted_columns_df: The DataFrame containing the split columns.
        :type splitted_columns_df: pandas.DataFrame
        :param group: A dictionary containing the query and other relevant details.
        :type group: dict
        :param dataframe: The original DataFrame containing the existing columns.
        :type dataframe: pandas.DataFrame
        :return: The update dataframe with new columns for splitted_columns_df,  and the updated group
        :rtype: dataframe, dict
        """
        try:
    
            unnamed_columns = []
            destination_columns = group.get("destination_columns", [])
            if not destination_columns :
                destination_columns=[]
            destination_columns = self.get_distinct_columns(destination_columns, dataframe)
            group['destination_columns'] = destination_columns
            # Check if the number of specified columns is less than the number of columns generated
            if len(destination_columns) < splitted_columns_df.shape[1]:
                i = 1
                while True:
                    column_name = f"new_column_{i}"
                    if column_name not in dataframe.columns:
                        unnamed_columns.append(column_name)
                        if len(unnamed_columns) == splitted_columns_df.shape[1] - len(destination_columns):
                            break
                    i += 1
                splitted_columns_df.columns = destination_columns + unnamed_columns
            else:
                # Use specified (or modified) column names for all columns, including "unnamed"
                splitted_columns_df.columns = destination_columns[:splitted_columns_df.shape[1]]
            if len(destination_columns) > splitted_columns_df.shape[1]:
                splitted_columns_df = splitted_columns_df.reindex(columns=destination_columns)
            return splitted_columns_df, group
        except Exception as e:
            logger.error(f"An error occured: Failed to get unique columns with splitted_columns_df: {splitted_columns_df}, group: {group} and dataframe: {dataframe}", exc_info=True)
            raise UtilsException("Failed to get unique columns.") from e


    @Logger.generate
    def generate_custom_date_format(self, date_format):
        """
        This method generates a custom date format string that can be used with Python's strftime function. The generated format string is based on the provided date format specification, which determines how dates should be formatted

        :param date_format: The input date format string 
        :type date_format: str
        :return: The custom date format string compatible with strftime
        :rtype: str
        """
        try:
            # Split the input date format into parts using '/', '-', '.' or space as separators
            date_parts = re.split(r'[ /.:\\-]', date_format)
            separators = re.findall(r"[ /.:\\-]", date_format)
            if separators != []:
                strftime_format_parts = []
                for date_part in date_parts:
                    strftime_format = self.common_mapping.get(date_part)
                    if strftime_format:
                        strftime_format_parts.append(strftime_format)
                    else:
                        strftime_format_parts.append(date_part)

                custom_date_format = ""
                for i in range(len(strftime_format_parts)):
                    custom_date_format += strftime_format_parts[i]
                    if i < len(separators):
                        custom_date_format += separators[i]
            else:
                custom_date_format = self.get_format(date_format)
            return custom_date_format
        except Exception as e:
            logger.error(f"An error occured: Failed to generate custom date format: {date_format}", exc_info=True)
            raise UtilsException("Failed to generate custom date format.") from e

    @Logger.generate
    def get_column_datatype_dict(self, dataframe):
        """
        This method retrieves the names of columns and their corresponding data types from the specified DataFrame
        :param dataframe: The Pandas DataFrame containing the data.
        :type dataframe: pandas.DataFrame
        :return: A list of dictionaries, each containing the column name and data type.
        :rtype: list
        """
        try:
            # Get the column names and their data types
            columns_info = []
            for column in dataframe.columns:
                column_info = {
                    "name": column,
                    "dataType": str(dataframe[column].dtype)
                }
                columns_info.append(column_info)
            return columns_info
        except Exception as e:
            logger.error(f"An error occured: Failed to get column data type dict with dataframe: {dataframe}", exc_info=True)
            raise UtilsException("Failed to get column data type dict.") from e

    @Logger.generate
    def generate_query(self, column, expr, value):
        """
        This method generates a query string based on the specified column name, a conditional expression, and a value. The generated query can be used to filter DataFrame according to the given parameters

        :param column: The name of the column to be queried.
        :type column: str
        :param expr: The expression to be applied 
        :type expr: str
        :param value: The value to be compared against the column.
        :type value: any
        :return: The generated query string.
        :rtype: str
        """
        try:
            expression = self.query_mapping.get(expr)
            query = expression.execute(column, value)
            return query
        except Exception as e:
            logger.error(f"An error occured: Failed to generate query with column: {column}, expr: {expr} and value: {value}", exc_info=True)
            raise UtilsException("Failed to generate query.") from e

    
    @Logger.generate
    def get_aggregate_function(self, aggregations):
        """
        This method converts a list of aggregation function names into their corresponding Pandas DataFrame methods. The resulting dictionary maps each aggregation function name to the corresponding method that can be used with a Pandas DataFrame for performing the aggregation
        :param aggregations: A list of aggregation function names as strings.
        :type aggregations: list
        :return: A list of Pandas DataFrame method names corresponding to the provided aggregation functions.
        :rtype: list
        """
        try:
            agg_funcs = []
            for agg_func in aggregations:
                if agg_func == "distinct":
                    agg_func = "nunique"
                if agg_func == "variance":
                    agg_func = "var"
                if  agg_func == "stddev":
                    agg_func = "std"
                agg_func = agg_func.lower()
                agg_funcs.append(agg_func)
            return agg_funcs
        except Exception as e:
            logger.error(f"An error occured: Failed to get aggrgate functions with {aggregations}", exc_info=True)
            raise UtilsException("Failed to get aggrgate functions.") from e

    @Logger.generate
    def get_format(self, date_format):
        """
        Converts a shorthand date format to a custom strftime format string

        :param date_format: The input date format, which may be a shorthand like "ymd".
        :type date_format: str
        :return: The corresponding strftime format string.
        :rtype: str
        """
        try:
            if date_format == "ymd":
                custom_format = "%Y%m%d"
            else:
                custom_format = date_format
            return custom_format
        except Exception as e:
            logger.error(f"An error occured: Failed to get format with {date_format}", exc_info=True)
            raise UtilsException("Failed to get format.") from e

    def generate_alias(self, dataframe_dict, alias_prefix):
        # Get a list of existing aliases
        existing_aliases = [info['alias'] for info in dataframe_dict.values()]

        # Use regex to find existing aliases that start with the given prefix and have a suffix number
        pattern = re.compile(f"{alias_prefix}_(\d+)")
        matching_aliases = [alias for alias in existing_aliases if pattern.match(alias)]

        if matching_aliases:
            # Extract the numeric part of each alias and find the highest number
            max_suffix = max(int(pattern.match(alias).group(1)) for alias in matching_aliases)
            next_suffix = max_suffix + 1
        else:
            # If no matching aliases are found, start with 1
            next_suffix = 1

        # Generate the new alias with incremented suffix
        new_alias = f"{alias_prefix}_{next_suffix}"
        
        return new_alias