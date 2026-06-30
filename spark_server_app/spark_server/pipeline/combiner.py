
from abc import ABC, abstractmethod
from pyspark.sql.functions import col
from .utilities import Utilities
from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
logger = Logger
util = Utilities()

class Combiner(ABC):
    @abstractmethod
    def execute(self, dataframes: dict, parameters: dict, output: dict, spark: str):
        pass


class Union(Combiner):
    @logger.generate
    def execute(self, dataframes, parameters, output, spark):
        try:
            logger.info("Performing union operation.")
            union_list = []
            for df in parameters['df_id']:
                if df in dataframes:
                    union_list.append(dataframes[df]["df"])
            if len(union_list) < 2:
                logger.debug("The length of the dataframe is less than 2")
                raise ValueError("At least two DataFrames are required for a union")
            union_df = union_list[0]
            for df in union_list[1:]:
                union_df, df = util.align_schemas(union_df, df)
                union_df = union_df.union(df)
            logger.info("Returning unioned dataframe.")
            output_file_id = output["df_id"]
            alias=output.get("dataframe_alias",None) #added by utkarsh
            dataframes.update({output_file_id: {"df": union_df,"alias":alias}})
            return dataframes
        except Exception as e:
            logger.error(f"Operation 'Union' completed with an exception: {str(e)}")
            raise CombinerException("Failed to perform union.")


class Join(Combiner):
    @logger.generate
    def execute(self, dataframes, parameters, output, spark):
        try:
            logger.info("Performing join operation.")
            groups = parameters["groups"]
            file1 = parameters['df_id'][0]
            file2 = parameters['df_id'][1]
            file1_name = parameters['file_names'][0].split('.')[1] if "." in parameters['file_names'][0] \
                else parameters['file_names'][0]
            file2_name = parameters['file_names'][1].split('.')[1] if "." in parameters['file_names'][1] \
                else parameters['file_names'][1]
            df1 = dataframes.get(file1)["df"]
            df2 = dataframes.get(file2)["df"]
            join_type = groups[0]["join_type"]
            left_on = groups[0]["left_on"]
            right_on = groups[0]["right_on"]
            left_on_cols = []
            right_on_cols = []
            # for each column in left and right on columns
            for left_col, right_col in zip(left_on, right_on):
                # if left and right columns are same
                if left_col == right_col:
                    # appending file names to left and right columns
                    left_col_new = left_col+"_"+file1_name
                    right_col_new = right_col+"_"+file2_name
                    left_on_cols.append(left_col_new)
                    right_on_cols.append(right_col_new)
                    # renaming left and right columns in respective dfs
                    df1 = df1.withColumnRenamed(left_col, left_col_new)
                    df2 = df2.withColumnRenamed(right_col, right_col_new)
                else:
                    left_on_cols.append(left_col)
                    right_on_cols.append(right_col)
            common_columns = set(df1.columns).intersection(set(df2.columns))

            # Add suffix "_enrollments" to common columns in df1
            df1 = df1.select(
                [col(col_name).alias(col_name + f"_{file1_name}") if col_name in common_columns else col_name for col_name
                 in df1.columns])
            # Add suffix "_students" to common columns in df2
            df2 = df2.select(
                [col(col_name).alias(col_name + f"_{file2_name}") if col_name in common_columns else col_name for col_name in
                 df2.columns])
            df1.createOrReplaceTempView("df1")
            df2.createOrReplaceTempView("df2")
            join_condition = " and ".join([f'df1.{left} = df2.{right}' for left, right in zip(left_on_cols,
                                                                                              right_on_cols)])
            # Perform the join using SQL query
            sql_query = f"SELECT * FROM df1 {join_type} JOIN df2 ON {join_condition}"

            # sql_query = f"SELECT * FROM df1 {join_type} JOIN df2 ON {join_condition}"
            joined_df = spark.sql(sql_query)
            output_file_id = output["df_id"]
            alias=output.get("dataframe_alias",None) #added by utkarsh
            dataframes.update({output_file_id: {"df": joined_df,"alias":alias}})
            logger.info("Returning joined dataframes.")
            return dataframes
        except Exception as e:
            logger.error(f"Operation 'Join' completed with an exception: {str(e)}")
            raise CombinerException("Failed to perform joins.")
