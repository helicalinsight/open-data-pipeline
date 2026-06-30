from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
#from session_variables import SessionVariables
#from environment import Environment
from helper.helper import *
import sys, os
from datetime import datetime
import pyspark.sql.functions as F

logger = Logger


class PyTool:
    #session_variables = SessionVariables.get()
    #env_variables = Environment.get_all()
    @logger.generate
    def execute(self, dataframes, parameters, spark, conf={}):
        try:
            logger.info(f"dataframes, parameters, spark {dataframes, parameters, spark}")
            base_path = os.path.abspath(os.path.join(__file__, "../../.."))
            package_path = os.path.join(base_path, "spark_server", "helper", "helper.py")
            sys.path.append(package_path)
            # Combine all the variables in a single scope
            global_scope = {'DataframeInformation': SparkDataframeInformation(dataframes),
                             'JobArguments': JobArguments(conf),
                             "datetime": datetime,
                            **vars(F)}
            #local_scope = {'df_collection': , 'job_arguments': conf}
            spark_code=parameters.get("spark_code")
            if spark_code:
                pycode=spark_code
            else:
                pycode = parameters["code"]
            exec(pycode, global_scope)
            return dataframes
        except Exception as e:
            logger.error(f"Operation 'PyTool' completed with an exception: {str(e)}")
            raise PyToolException("Failed to execute PyTool.") from e
