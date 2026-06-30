import typing
from typing import Dict, Union
from .extractor import *
from .transformer import *
from .combiner import *
from .loader import *
from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
from .dataframes import Dataframes
from .pytool import PyTool

df = Dataframes()

logger = Logger


class Processor:

    def __init__(self):
        self.operation_mapping: Dict[str, typing.Union[Transformer, Loader, Combiner, Extractor, PyTool]] = {
            "add_columns": AddColumns,
            "aggregate": Aggregations,
            "concat": Concat,
            "correlation": Correlation,
            "date_format": DateFormat,
            "deduplicate": Deduplicate,
            "drop_all_columns_except": DropAllColumnsExcept,
            "drop_columns": DropColumns,
            "drop_na": DropNa,
            "export": Export,
            "expression": Arithmetic,
            "extract": Extract,
            "export_table": ExportTables,
            "fill_na": FillNa,
            "filter_value": Filter,
            "joins": Join,
            "lower_case": LowerCase,
            "pytool": PyTool,
            "read_files": ReadFiles,
            "read_tables": ReadTables,
            "read": ReadS3,
            "delete_files": DeleteFile,
            "rearrange_columns": RearrangeColumns,
            "rename_columns": RenameColumns,
            "replace_special_characters": ReplaceSpecialCharacters,
            "sort": Sort,
            "split": Split,
            "sql": SQLOperations,
            "trim": Trim,
            "union": Union,
            "upper_case": UpperCase,
            "when_otherwise": WhenOtherwise,
            "typecast": Cast
        }

    @logger.generate
    def process(self, pipeline, connection_id, spark, schedule_conf, config=None):
        if config is None:
            config = {}
        try:
            dataframes = df.get()
            logger.debug("processing data..")
            for index, step in enumerate(pipeline):
                operation = step["function"]
                parameters = step["parameters"] # parameters passed in the step yaml
                parameters["user_id"] = schedule_conf["user_id"]
                parameters["chat_id"] = schedule_conf["chat_id"]
                conf = config.get(f'__{operation}__{index}', {})
                output = step.get("output", None) # If there is output expected for the step, output section will have details for the cache document
                
                operation_class = self.operation_mapping.get(operation, None)

                if operation_class is None:
                    raise Exception("Operation class not implemented")
                
                if operation_class == ReadFiles or operation_class == ReadTables or operation_class == ReadS3:
                    dataframes = operation_class().execute(
                        parameters, connection_id, output, spark, conf, aod_audit_instance=schedule_conf.get("AodAudit", None))
                    # if output:
                    #     dataframes[df[output]] = dataframes
                    # else:
                    #     dataframes[df_id] = operation_class().execute(dataframes[df_id], parameters, spark)
                    df.update(dataframes)
                    df.get()
                elif operation_class == DeleteFile:
                    df.dataframes_dict.pop(parameters.get("source_id"), None)

                elif operation_class == Export or operation_class == ExportTables:
                    conf = config.get(f'__export__', {})
                    logger.debug("Exporting data..")
                    dataframes = df.get()
                    operation_class().execute(dataframes=dataframes, parameters=parameters, connection_id=connection_id, spark=spark, schedule_conf=schedule_conf, config=conf)
                elif operation_class == PyTool:
                    logger.debug("Executing pytool....")
                    dataframes = df.get()
                    dataframes = operation_class().execute(dataframes=dataframes, parameters=parameters, spark=spark, conf=config)
                    df.update(dataframes)
                else:
                    if operation_class == Union or operation_class == Join:
                        dataframes = df.get()
                        dataframes = operation_class().execute(dataframes=dataframes, parameters=parameters, output=output, spark=spark)
                        df.update(dataframes)
                    else:
                        df_id = parameters['df_id']
                        dataframes = df.get()
                        if df_id not in dataframes or "df" not in dataframes[df_id] or dataframes[df_id]["df"] is None:
                            raise Exception(f"df_id {df_id} does not have valid value in dataframes {dataframes}")
                        
                        audit_config = {
                            "schedule_id": schedule_conf.get("schedule_id", ""),
                            "run_id": schedule_conf.get("run_id", ""),
                            "function": step.get("function", ""),
                            "chat_id": schedule_conf.get("chat_id", ""),
                            "user_id": schedule_conf.get("user_id", ""),
                            "execution_type": schedule_conf.get("execution_type", "pipeline")
                        }
                        df_out = operation_class(audit_config).execute_with_audit(dataframes[df_id]["df"], parameters, spark)
                        # df_out = operation_class().execute(dataframes[df_id]["df"], parameters, spark)
                        if output:
                            alias=output.get("dataframe_alias")
                            dataframes[output["df_id"]] = {"df": df_out,"alias":alias} #added by utkarsh
                        else:
                            dataframes[df_id]["df"] = df_out
                        df.update(dataframes)
            
            return dataframes
        except Exception as e:
            logger.error(f"Operation completed with exception: {str(e)}")
            raise ProcessorException("Failed to process the data.") from e

