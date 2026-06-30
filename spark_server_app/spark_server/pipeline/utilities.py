from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
import re
from ..configurations.baseConfig.config import localDirectory
import os
from .query_generator import *
from pyspark.sql.types import *
from pyspark.sql.functions import *

logger = Logger

class Utilities:
    def __init__(self) -> None:
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
        self.format_mapping = {
            # years
            'YYYY': 'y', 'yyyy': 'y', 'Y': 'y', 'YY': 'y',
            'yy': 'yy', 'y': 'y',  # two digit year

            # months
            'mm': 'MM', 'm': 'M',

            # names of months
            'mmm': 'MMM', 'MMM': 'MMM',

            # full month name
            'mmmm': 'MMMM', 'MMMM': 'MMMM',

            # days
            'dd': 'dd', 'd': 'd', 'DD': 'd', 'DD,': 'd,', 'd,': 'd,', 'D': 'd',

            # week days
            'ddd,': 'E,', 'dddd': 'E',

            # hours
            'H': 'H', 'HH': 'H', 'hh': 'H', 'h': 'H',

            # minutes
            'MM': 'm', 'M': 'm',

            # seconds
            'SS': 's', 'ss': 's', 'S': 's',

            # AM/PM
            'AP': 'a', 'ap': 'a'
        }
        self.bool_mapping = {'true': True,  '1': True, 1: True,
                             'false': False, '0': False, 0: False}

        self.cast_mapping = {
                "integer": IntegerType(),
                "float": FloatType(),
                "bool": BooleanType(),
                "boolean": BooleanType(),
                "date": DateType(),
                "timestamp": TimestampType(),
                "string": StringType()
            }

    @logger.generate
    def is_unix(self, columns, dataframe):
        try:
            unix_pattern = r'^-?\d+(\.\d{1,3})?$'
            # Check if any of the columns contain unix time values
            for column in columns:
                if dataframe.select(regexp_extract(col(column).cast("string"), unix_pattern, 0).alias(column)).filter(col(column) != "").count() > 0:
                    return True
            return False
        except Exception as e:
            logger.error(f"Operation 'check_unix' executed with exception: columns: {columns} and dataframe: {dataframe}")
            raise UtilsException("Failed to check unix format.") from e
        
    @logger.generate
    def convert_to_bool(self, value):
        try:
            # Convert value to string, lower case it, and lookup in mapping
            value_str = str(value).lower()
            return self.bool_mapping.get(value_str, value)
        except Exception as e:
            logger.error(f"Operation 'convert_to_bool' executed with exception: value: {value}")
            raise UtilsException("Failed to convert to bool.") from e
    
    def trim_string(self, location, num_chars, input_str):
        try:
            if input_str is None:
                return None
            if location == 'left':
                return input_str[num_chars:]
            elif location == 'right':
                return input_str[:-num_chars]
            else:
                logger.debug("location must be 'left' or 'right'")
                raise Exception
        except Exception as e:
            logger.error(f"Operation 'trim_string' executed with exception: location: {location}, num_chars: {num_chars} and input_str: {input_str}")
            raise UtilsException("Failed to trim.") from e

    @logger.generate
    def get_unmapped_values(self, columns, dataframe):
        try:
            unmapped_values = {}
            for col in columns:
                unmapped_values[col] = dataframe[~dataframe[col].isin([True, False])][col].tolist()
            unmapped_values = [f"{col} contains {list(set(values))}" for col, values in unmapped_values.items()]
            unmapped_values_text = ', '.join(unmapped_values)
            return unmapped_values_text
        except Exception as e:
            logger.error(f"Operation 'get_unmapped_values' executed with exception: columns: {columns} and dataframe: {dataframe}")
            raise UtilsException("Failed to get unmapped values.")from e
        
    @logger.generate
    def generate_custom_date_format(self, date_format):
        # Used in date_format function
        # If we have the date format 'MM/dd/yyyy' then this will be in pandas format so splitting this and then mapping to respective spark format here.
        
        try:
            # Split the input date format into parts using '/', '-', '.' or space as separators
            date_parts = re.split(r'[ /.:\\-]', date_format)
            separators = re.findall(r"[ /.:\\-]", date_format)
            if separators != []:
                strftime_format_parts = []
                for date_part in date_parts:
                    strftime_format = self.format_mapping.get(date_part)
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
                # if we dont have seperators using regex generating custome format
                pattern = re.compile('|'.join(re.escape(key) for key in sorted(self.format_mapping.keys(), key=len, reverse=True)))
                custom_date_format = pattern.sub(lambda x: self.format_mapping[x.group()], date_format)
            return custom_date_format
        except Exception as e:
            logger.error(f"Operation 'generate_custom_date_format' executed with exception: date_format: {date_format}")
            raise UtilsException("Failed to generate custom date format.")from e
    
    @logger.generate
    def infer_date_format(self, date_strings):
        try:
            patterns = [
                    (r'^[A-Za-z]{3}, [A-Za-z]{3} \d{1,2}, \d{4} \d{2}:\d{2}:\d{2}$', 'ddd, MMM DD, YYYY HH:MM:SS'),
                    (r'^\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', 'yy-mm-dd HH:MM:SS'),
                    (r'^\d{4}-\d{2}-\d{2}$', 'yyyy-mm-dd'),
                    (r'^\d{4}-\d{2}-\d{2}$', 'YYYY-mm-DD'),
                    (r'^[A-Za-z]{3} \d{1,2}, \d{4}$', 'MMM d, YYYY'),
                    (r'^\d{4}/\d{2}/\d{2}$', 'YYYY/mm/DD'),
                    (r'^\d{2}-\d{2}-\d{4}$', 'DD-mm-YYYY'),
                    (r'^\d{2}\.\d{2}\.\d{4}$', 'DD.mm.YYYY'),
                    (r'^\d{1,2} [A-Za-z]+ \d{4}$', 'd MMMM YYYY'),
                    (r'^\d{1,2} [A-Za-z]+$', 'd MMMM'),
                    (r'^\d{1,2} [A-Za-z]+$', 'd MMMM'),
                    (r'^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}$', 'y-m-d H:M:S'),
                    (r'^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}$', 'Y-m-D H:M:S'),
                    (r'^\d{8}$', 'ymd'),
                    ('^\d{1,2}/\d{1,2}/\d{4}$', 'M/d/yyyy'),
                    ('\d{1,2}-\d{1,2}-\d{4}$', 'M-d-yyyy'),
                ]
            for pattern, date_format in patterns:
                filtered_date_strings = [date_str for date_str in date_strings if date_str is not None]
                if all(re.match(pattern, date_str) for date_str in filtered_date_strings):
                    return date_format
        except Exception as e:
            logger.error(f"Operation 'infer_date_format' executed with exception: date_strings: {date_strings}")
            raise UtilsException("Failed to infer date format.")from e

    @logger.generate
    def convert_to_date_format(self, date_format):
        try:
            # Define a mapping of date components to Spark format components
            format_mapping = {
                'YYYY': 'yyyy',  # Year
                'MM': 'MM',  # Month
                'DD': 'dd',  # Day
                'HH': 'HH',  # Hour
                'mm': 'mm',  # Minute
                'ss': 'ss'  # Second
            }
            separator_match = re.search(r'[^a-zA-Z0-9]', date_format)
            separator = separator_match.group() if separator_match else ''

            components = re.split(r'[^a-zA-Z]+', date_format)
            spark_format = separator.join([format_mapping.get(component, component) for component in components])

            return spark_format
        except Exception as e:
            logger.error(f"Operation 'convert_to_date_format' executed with exception: date_format: {date_format}")
            raise UtilsException("Failed to convert to spark date format.")from e

    @logger.generate
    def create_export_path(self, user_id,chat_id,file_name):
    #def create_export_path(self, df_id,file_name):
        try:
            base_path=localDirectory._path
            # base_path = os.path.abspath(base_path)
            final_path = os.path.join(base_path, user_id,"output",chat_id)
            #final_path = os.path.join(base_path, df_id,"output")
            final_path = os.path.normpath(final_path)
            os.makedirs(final_path, exist_ok=True)
            file_path = os.path.join(final_path, file_name)
            return file_path
        except Exception as e:
            logger.error(f"Operation 'create_export_path' executed with exception: user_id: {user_id}, chat_id: {chat_id} and file_name: {file_name}")
            raise UtilsException("Failed to generate export path.")from e
        
    @logger.generate
    def get_aggregate_function(self, aggregations):
        try:
            agg_funcs = []
            for agg_func in aggregations:
                if agg_func == "distinct":
                    agg_func = "countDistinct"
                if agg_func == "median":
                    agg_func = "percentile_approx"
                agg_funcs.append(agg_func)
            return agg_funcs
        except Exception as e:
            logger.error(f"Operation 'get_aggregate_function' executed with exception: aggregations: {aggregations}")
            raise UtilsException("Failed to get aggregate function.")from e
    
    def generate_query(self, column, expr, value):
        try:
            expression = self.query_mapping.get(expr)
            query = expression.execute(column, value)
            return query
        except Exception as e:
            logger.error(f"Operation 'generate_query' executed with exception: column: {column}, expr: {expr} and value: {value}")
            raise UtilsException("Failed to generate query.") from e

    # TODO: This has to be added to helper (this code is already present in pandas code)    
    def clean_column_name(self, col_name: str) -> str:
        """Clean a single column name by converting to lowercase and replacing non-alphanumeric characters with underscores."""
        return re.sub('[^0-9a-zA-Z]+', '_', col_name.strip().lower())

    # Align schemas - make sure all DataFrames in the union list have the same columns
    def align_schemas(self, df1, df2):
        # Get the set of columns in each DataFrame
        cols_df1 = set(df1.columns)
        cols_df2 = set(df2.columns)
        
        # Add missing columns to df1
        for col in cols_df2.difference(cols_df1):
            df1 = df1.withColumn(col, lit(None))
        
        # Add missing columns to df2
        for col in cols_df1.difference(cols_df2):
            df2 = df2.withColumn(col, lit(None))
        
        # Reorder columns to match
        df1 = df1.select(*df2.columns)
        
        return df1, df2
    
    def escape_special_chars(self, input_string):
        return re.sub(r'([^\w\s])', r'\\\1', input_string)
