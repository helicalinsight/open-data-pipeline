from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
from .utilities import Utilities
from abc import ABC, abstractmethod
from pyspark.sql.functions import *
#from pyspark.sql.window import *
import re
from functools import reduce
from pyspark.sql import DataFrame
from pyspark.sql.types import *
from ..audit_log.utils import audit_usage_decorator

util = Utilities()
logger = Logger


class Transformer(ABC):
    def __init__(self, conf=None):
        if conf is None:
            conf = {}
        self.schedule_id = conf.get('schedule_id', None)
        self.run_id = conf.get('run_id', None)
        self.intent_name = conf.get('function', None)
        self.user_id = conf.get('user_id', None)
        self.chat_id = conf.get('chat_id', None)
        self.execution_type = conf.get('execution_type', "pipeline")

    @abstractmethod
    def execute(self, dataframe: DataFrame, parameters: dict, spark) -> DataFrame:
        pass

    @audit_usage_decorator()
    def execute_with_audit(self, dataframe: DataFrame, parameters, spark) -> DataFrame:
        return self.execute(dataframe, parameters, spark)

class AddColumns(Transformer):
    """
        "groups": [{"columns": ["school"], "default": "MNS"}]
    """
    @logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict, spark) -> DataFrame:
        try:
            for group in parameters["groups"]:
                for add_column in group['columns']:
                    default = group.get('default', None)
                    if default is not None:
                        dataframe = dataframe.withColumn(add_column, lit(default))
                    else:
                        dataframe = dataframe.withColumn(add_column, lit(None).cast(StringType()))
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'AddColumns' completed with an exception: dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to add columns.") from e


class RenameColumns(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        try:
            for group in parameters["groups"]:
                dataframe = dataframe.withColumnRenamed(group['old_name'], group['new_name'])
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'RenameColumns' completed with an exception: dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to rename columns.") from e


class Sort(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        try:
            for group in parameters["groups"]:
                dataframe = dataframe.sort(group['columns'], ascending=[group['ascending']])
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'sort' completed with an exception: dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to sort columns.") from e


class Deduplicate(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        try:
            for group in parameters["groups"]:
                dataframe = dataframe.dropDuplicates(group['columns'])
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'deduplicate' completed with an exception: dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to deduplicate.") from e


class Concat(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        """
            "groups": [{"columns": ["age", "marks"], "separator": "/", "destination_column": "code"}]
        """
        try:
            for group in parameters["groups"]:
                destination_column = group.get("destination_column")
                separator = group.get("separator")
                dataframe = dataframe.withColumn(destination_column, concat_ws(separator, *[col(x) for x in group["columns"]]))              
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'concat' completed with an exception: dataframe :{dataframe} and parameters :{parameters} - {e}") 
            raise DataTransformationException(f"Failed to concat.") from e

class ReplaceSpecialCharacters(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        """
             "groups": [{"target_character": "_",
             "columns": ["name"],
             "replacement_character": "-"}
        ]
            """
        try:
            for group in parameters["groups"]:
                group["replacement_character"] = util.escape_special_chars(group["replacement_character"])
                dataframe = dataframe.withColumn(group["columns"][0], regexp_replace(group["columns"][0],
                                                group["target_character"], group["replacement_character"]))
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'ReplaceSpecialCharacter' completed with a dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to replace special characters.") from e


class Split(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        """
            {"groups": [{"destination_columns": ["first_name", "last_name"], 
                                  "column": "name", 
                                  "delimiter": "_"}]}
        """
        try:
            for group in parameters["groups"]:
                # to get unique destination columns if they already exists in dataframe
                destination_columns = group.get("destination_columns")
                for index, column_name in enumerate(destination_columns):                
                    dataframe = dataframe.withColumn(column_name,
                                                    split(group["column"], group["delimiter"]).getItem(index))
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'Split' completed with an exception: dataframe :{dataframe} and parameters :{parameters}") 
            raise DataTransformationException(f"Failed to split columns.") from e



class DropColumns(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        """
             "groups": [ {"columns": ["order-id"]}, {"columns": ["amount_maximum"]}
        """
        try:
            for group in parameters["groups"]:
                dataframe = reduce(lambda df, col_name: df.drop(col(col_name)), group["columns"], dataframe)
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'DropColumns' completed with an exception: dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to drop columns.") from e



class DropAllColumnsExcept(Transformer):
    @logger.generate
    def execute(self, dataframe: DataFrame, parameters: dict, spark) -> DataFrame:
        """
             "groups": [{"columns": ["amount", "value"]}]
        """
        try:
            for group in parameters["groups"]:
                columns = group["columns"]
                columns_to_drop = [column for column in dataframe.columns if
                                        column not in columns]
                dataframe = reduce(lambda df, col_name: df.drop(col(col_name)), columns_to_drop, dataframe)
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'DropAllColumnsExcept' completed with an e dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to drop all columns except the given columns.") from e
    
    
class DateFormat(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        """
             "groups":  [{"columns": ["order_date"],"format": "YYYY-MM-DD"}]
        """
        try:
            for group in parameters["groups"]:
                date_columns = [col for col in group['columns'] if isinstance(dataframe.schema[col].dataType, DateType)]
                if not date_columns:
                    for col_name in group['columns']:
                        # Casting the column to DateType
                        casted_col = dataframe.withColumn(col_name, col(col_name).cast(DateType()))
                        # Checking if the column is actually of DateType
                        if isinstance(casted_col.schema[col_name].dataType, DateType):
                            date_columns.append(col_name)
                new_format =  util.generate_custom_date_format(group.get("format"))           
                dataframe = reduce(
                    lambda df, col_name: df.withColumn(
                        col_name, date_format(df[col_name], new_format)
                    ), group["columns"], dataframe)
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'DateFormat' completed with an exception:  dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to change the date format.") from e


class WhenOtherwise(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        """
             "groups":  [{"query": "SELECT *, CASE\n\tWHEN amount > 100 THEN 'PASS'\n\tWHEN amount = 20 THEN
             'JUST PASS'\n\tELSE 'FAIL'\nEND AS final_res23\nFROM df;"}]
        """
        try:
            for group in parameters["groups"]:
                sql_query = group["query"]
                case_pattern = re.compile(r'\bCASE\b\s*(.*?)\bEND\b', re.DOTALL)
                case_part = case_pattern.search(sql_query).group(0).strip()
                alias_pattern = re.compile(r'\bEND AS (`?)(\w+)\b')
                alias_name = alias_pattern.search(sql_query).group(2)
                dataframe = dataframe.withColumn(alias_name, expr(case_part))
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'WhenOtherwise' completed with an exceptio dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to perform WhenOtherwise.") from e



class Filter(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        """
             "groups": [{"columns": ["name"], "expr":"equals", "value":["Bob"]}]
        """
        try:
            for group in parameters["groups"]:
                columns = group.get('columns')
                expr = group.get('expr')
                value = group.get('value')
                if columns and expr:
                    for column in columns:
                        query = util.generate_query(column, expr, value)
                        dataframe = dataframe.filter(query)
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'Filter' completed with an exception: dataframe :{dataframe} and parameters :{parameters}") 
            raise DataTransformationException(f"Failed to perform Filter.") from e



class UpperCase(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        """
            "groups": [{"columns": ["name"]}, {"columns": ["city"]}]
        """
        try:
            for group in parameters["groups"]:
                for column in group["columns"]:
                    dataframe = dataframe.withColumn(column, upper(dataframe[column]))
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'UpperCase' completed with an exception: dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to perform Uppercase.") from e


class LowerCase(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        """
            "groups": [{"columns": ["name"]}, {"columns": ["city"]}]
        """
        try:
            for group in parameters["groups"]:
                for column in group["columns"]:
                    dataframe = dataframe.withColumn(column, lower(dataframe[column]))
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'LowerCase' completed with an exception: dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to perform LowerCase.") from e


class Trim(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        """
            "groups": [{"columns": ["name"], "location": "right", "number_of_characters": 1}]
        """
        try:
            for group in parameters["groups"]:
                for column in group["columns"]:
                    location = group["location"]
                    number_of_characters = group["number_of_characters"]
                    # Apply conditional logic based on 'location'
                    if location == "left":
                        start_position = 1  # Start from the left
                    elif location == "right":
                        start_position = f"length(`{column}`) - {number_of_characters} + 1"  # Start from the right
                    else:
                        raise ValueError("Location must be 'left' or 'right'")

                    dataframe = dataframe.withColumn(column, expr(f"substring(`{column}`, {start_position}, {number_of_characters})"))
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'Trim' completed with an exception: dataframe :{dataframe} and parameters :{parameters}") 
            raise DataTransformationException(f"Failed to perform Trim.") from e
        
    
class RearrangeColumns(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        """
            "groups": [{"columns": ['id', 'grade', 'name']}]
        """
        try:
            for group in parameters["groups"]:
                rearrange_params = group.get('columns')
                rearrange_params = sorted(rearrange_params, key=lambda x: list(x.values())[0])
                reference_index = 0
                for i in range(0, len(rearrange_params)):
                    param_column_name = list(rearrange_params[i].keys())[0]
                    param_column_index = rearrange_params[i][param_column_name]
                    total_cols = len(dataframe.columns) - 1
                    current_index = [col for col in dataframe.columns].index(param_column_name)
                    # case for moving column to last position
                    if param_column_index <= -1:
                        new_column_index = total_cols + param_column_index + 1
                    # case for moving column to first position, having one column
                    if param_column_index == 0 and len(rearrange_params)==1:
                        new_column_index = 0
                        reference_index = current_index
                    # case for moving column to first position, having multiple columns
                    if param_column_index == 0 and len(rearrange_params)>1:
                        reference_column = param_column_name
                        reference_index = current_index
                        new_column_index = reference_index
                    # case for last element
                    if reference_index == total_cols and param_column_index > 0:
                        new_column_index = param_column_index + reference_index - 1
                    # case for first element
                    if reference_index == 0 and param_column_index > 0:
                        new_column_index = param_column_index + reference_index
                    # case for middle elements
                    if reference_index != 0 and reference_index < total_cols and param_column_index > 0:
                        new_column_index = param_column_index + reference_index
                    # case for middle elements but after the reference element
                    if reference_index != 0 and reference_index < total_cols and param_column_index > 0 and current_index < reference_index:
                        reference_index = [col for col in dataframe.columns].index(reference_column)
                        new_column_index = param_column_index + reference_index - 1
                    columns = dataframe.columns
                    columns.remove(param_column_name)
                    columns.insert(new_column_index, param_column_name)
                    dataframe = dataframe.select(*columns)
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'RearrangeColumns' completed with an excep dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to perform RearrangeColumns.") from e


class SQLOperations(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        """
           "groups": [{"query": "SELECT * FROM df"}]
        """
        try:
            for group in parameters["groups"]:
                dataframe.createOrReplaceTempView("df")
                dataframe = spark.sql(group["query"])
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'SQLOperations' completed with an exceptio dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to perform SQLoperations.") from e
    

class DropNa(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        """
           None or "groups": [{"subset":['name', 'toy']}]
        """
        try:
            if not parameters:
                dataframe = dataframe.dropna()
            else:
                for group in parameters["groups"]:
                    dataframe = dataframe.dropna(subset=group["subset"])
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'DropNa' completed with an exception: dataframe :{dataframe} and parameters :{parameters}") 
            raise DataTransformationException(f"Failed to perform DropNa.") from e
    


class Extract(Transformer):
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        """
        "groups": [{"column": "joining_date", "component": ["year"], "destination_column": "joining_year"}]
        """
        try:
            for group in parameters["groups"]:
                if group["component"][0] == "year":
                    dataframe = dataframe.withColumn(group["destination_column"], year(dataframe[group["column"]]))
                elif group["component"][0] == "month":
                    dataframe = dataframe.withColumn(group["destination_column"], month(dataframe[group["column"]]))
                elif group["component"][0] == "day":
                    dataframe = dataframe.withColumn(group["destination_column"], dayofmonth(dataframe[group["column"]]))
                return dataframe
        except Exception as e:
            logger.error(f"Operation 'Extract' completed with an exception: dataframe :{dataframe} and parameters :{parameters}") 
            raise DataTransformationException(f"Failed to perform extract.") from e


class Arithmetic(Transformer):
    """
    "groups": [{"query": "units_sold+5", "destination_column": "units_total"}]
    """
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        try:
            for group in parameters["groups"]:
                query = group["query"]
                destination_column = group["destination_column"]
                if "//" in query:
                    query = group["query"].replace("//", "/")
                    dataframe = dataframe.withColumn(destination_column, floor(expr(query)))
                elif "**" in query:
                    base, exponent = query.split("**")
                    base = base.strip()
                    exponent = exponent.strip()
                    dataframe = dataframe.withColumn(destination_column, pow(expr(base), expr(exponent)))
                else:
                    dataframe = dataframe.withColumn(destination_column, expr(query))
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'Arithmetic' completed with an exception:  dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to perform arithmetic.") from e
    

class Aggregations(Transformer):
    """
    "groups": [
                {
                    "columns": ["value1", "value2"],
                    "destination_columns": [],
                    "agg": ["sum"],
                    "group_by": ["category", "subcategory"],
                }
            ]
    """
    # median is not supported in pyspark 3.3.3 and  approxQuantile is also not working
    # tried to use percentile_approx the values are differing from pandas
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        try:
            for group in parameters["groups"]:
                agg_exprs = []
                index=0
                for col_name in group["columns"]:
                    agg_functions = util.get_aggregate_function(group['agg'])
                    for agg_func in agg_functions:
                        func = globals()[agg_func]  # Get the function from the string name
                        if group["destination_columns"]:
                            alias_name = group["destination_columns"][index]
                        else:
                            alias_name = f"{agg_func}_{col_name}"
                        index += 1
                        #if agg_func == "percentile_approx":
                            #agg_exprs.append(func(col(col_name), 0.5).alias(alias_name))
                        #else:
                        agg_exprs.append(func(col(col_name)).alias(alias_name))
                agg_df = dataframe.groupBy(group["group_by"]).agg(*agg_exprs)
                # using crossjoin to retain original dataframe if groupby is not present
                empty_groups_by = [group for group in parameters["groups"] if not group["group_by"]]
                if empty_groups_by:
                    dataframe = dataframe.crossJoin(agg_df)
                else:
                    dataframe = agg_df
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'Aggregations' completed with an exception: dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to perform aggregations.") from e
    

class Cast(Transformer):  
    @logger.generate 
    def execute(self, dataframe, parameters, spark):
        try:
            for group in parameters["groups"]:
                columns = group["columns"]
                new_type = group["new_type"]
                if new_type in ["date", "timestamp"]:
                    is_unix = "unix" if util.is_unix(columns, dataframe) is True else None
                    old_type = group.get('old_type') if group.get('old_type') else is_unix
                    if old_type == "unix":
                        new_type = util.cast_mapping.get(group["new_type"])
                        for column in columns:
                            if any(len(str(row[0]))>10 for row in dataframe.select(column).collect()):
                                # for ms unix formats
                                dataframe = dataframe.withColumn(column, to_date(from_unixtime((col(column).cast("long") / 1000), 'yyyy-MM-dd HH:mm:ss')))
                            else:
                                dataframe =  dataframe.withColumn(column, to_date(from_unixtime(col(column)), 'yyyy-MM-dd HH:mm:ss'))
                    else:
                        for column in columns:    
                            if old_type is None:
                                # If old type is None and we do not infer it gives None 
                                old_type = util.infer_date_format([row[0] for row in dataframe.select(column).collect()])
                            old_type = util.generate_custom_date_format(old_type)                     
                            dataframe=dataframe.withColumn(column, to_date(col(column),old_type))                      
                else:
                    if new_type in ["float", "integer"]:
                        new_type = util.cast_mapping.get(group["new_type"])
                        for column in columns:
                            dtype = [dtype for name, dtype in dataframe.dtypes if name == column][0]
                            if dtype == "float" and new_type == "integer":
                                dataframe = dataframe
                            else:
                                dataframe = dataframe.withColumn(column, col(column).cast(new_type))
                    elif new_type in ["string", "bool", "boolean", 'object']:
                        if new_type in ["bool", "boolean"]:
                            for col_name in group['columns']:
                                bool_udf = udf(util.convert_to_bool, BooleanType())
                                dataframe = dataframe.withColumn(col_name, bool_udf(col(col_name)))
                        else:
                            for column in columns:
                                dtype = [dtype for name, dtype in dataframe.dtypes if name == column][0]
                                # Applying initcap to "true" or "false" converts them to "True" or "False"
                                # Because in pandas we have True and False so to match that converting here
                                if dtype == "boolean":
                                    dataframe = dataframe.withColumn(column, col(column).cast(new_type))
                                    dataframe = dataframe.withColumn(column, initcap(dataframe[column]))
                                else:
                                    dataframe = dataframe.withColumn(column, col(column).cast(new_type))
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'Cast' completed with an exception:{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to perform cast.") from e


class FillNa(Transformer):   
    @logger.generate 
    def execute(self, dataframe, parameters, spark):
        try:
            for group in parameters["groups"]:
                column = group.get("column", "")
                if column:
                    if "value" in group and group["value"] is not dict:
                        dataframe = dataframe.fillna({column: group["value"]})
                else:                    
                    if "value" in group and group["value"] is not dict:
                        dataframe = dataframe.fillna(group["value"])
                    elif "value" in group and group["value"] is dict:
                        dataframe = dataframe.fillna(group["value"])
                    elif "value" in group and "axis" in group:
                        dataframe = dataframe.fillna(group["value"], axis=1)
                    elif "method" in group:
                        logger.info("Method not implemented")
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'FillNa' completed with an exception: dataframe :{dataframe} and parameters :{parameters}") 
            raise DataTransformationException(f"Failed to perform FillNa.") from e


class Correlation(Transformer):
    """
        "groups": [ {"columns": ["age", "marks"],  "destination_column":"age-marks-correlation"}]
    """
    @logger.generate
    def execute(self, dataframe, parameters, spark):
        try:
            for group in parameters["groups"]:
                if len(group["columns"]) == 2:
                    correlation = dataframe.stat.corr(group["columns"][0], group["columns"][1])
                    dataframe = dataframe.withColumn(group["destination_column"], lit(correlation))
                else:
                    logger.debug("Two columns are required for correlation")
                    raise Exception
            return dataframe
        except Exception as e:
            logger.error(f"Operation 'Correlation' completed with an exception: dataframe :{dataframe} and parameters :{parameters}")
            raise DataTransformationException(f"Failed to perform correlation.") from e

