import sys
from spark_server.logger.logger import Logger, logger, set_logging_level
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from spark_server.configurations.mongo_to_yaml_translator import MongoToYamlTranslator
from spark_server.configurations.mongo_to_yaml_translator import ExportPipeline
from spark_server.configurations.prepare_connection_id import PrepareConnectionId
from spark_server.configurations.configuration import Configuration
from spark_server.configurations.replace_connections import ReplaceConnections
from spark_server.pipeline.manager import Manager
from spark_server.exceptions.exceptions import *
from spark_server.file_operations.read import Read
import yaml
from spark_server.configurations.baseConfig.config import localDirectory
import re
from helper.helper import create_file_operations, create_dataframe_operations,SparkReadOrWriteFiles, SparkDataframeInformation, JobArguments, Connection

# aod_spark_context, aod_spark_frame and audit_tracker are volume mounts
from odp_code_context.aod_spark_context import AodSparkContext
from odp_code_context.aod_spark_frame import AodSparkFrame
from audit_tracker.audit_tracker import AuditTracker, ScheduleRunContext
import textwrap
from spark_server.configurations.mongo_to_yaml_translator import mongo_audit_runs, mongo_audit_usage

read = Read()
mongo_to_yaml = MongoToYamlTranslator()
prepare_connection_id = PrepareConnectionId()
configuration = Configuration()
replace_connections = ReplaceConnections()

def _wrap_custom_libraries(code: str) -> str:
    """
    Receives a code string which represents code added in ACE editor by user.
    We provide two custom classes to users, "AodSparkContext" (similar to spark 
    context) and "AodSparkFrame" (similar to pyspark.sql.DataFrame).
    
    This functions injects necessary context in the code string so that these
    classes are usable.
    """
    import_str = textwrap.dedent("""
        from odp_code_context.aod_spark_context import AodSparkContext
        from odp_code_context.aod_spark_frame import AodSparkFrame
    """)
    wrapped_code = f"{import_str}\n{code}"
    return wrapped_code

def _get_connection_specific_spark_conf(connection_id_dict):
    """
    Get connection-specific Spark configuration based on connection types.
    
    Args:
        connection_id_dict (dict): Dictionary of connection configurations
        
    Returns:
        dict: Spark configuration settings for all connection types
    """
    spark_conf_dict = {}
    
    for conn_id, conn_details in connection_id_dict.items():
        if (conn_details.get('type') == 'database' and 
            conn_details.get('details', {}).get('type') == 'couchbase'):
            
            logger.info(f"Found Couchbase connection: {conn_id}")
            couchbase_connection = conn_details['details']
            
            # Get values from connection details
            host = couchbase_connection.get('host')
            username = couchbase_connection.get('username') 
            password = couchbase_connection.get('password')
            bucket = couchbase_connection.get('bucket')
            
            if host and username and password and bucket:
                # Build connection string WITHOUT port
                connection_string = f"couchbase://{host}"
                
                # Set Couchbase configuration in SparkConf
                spark_conf_dict.update({
                    "spark.couchbase.connectionString": connection_string,
                    "spark.couchbase.username": username,
                    "spark.couchbase.password": password,
                    "spark.couchbase.implicitBucket": bucket
                })
                
                logger.info(f"Configured Couchbase Spark settings for host: {host}")
            else:
                logger.warning("Missing required Couchbase connection parameters")
    
    return spark_conf_dict


def extract_couchbase_from_code(code_str: str) -> dict:
    """
    Extract Couchbase configs from ACE code using regex.
    Assumes plain string literals like:
      COUCHBASE_HOST = "164.52.218.57"
      
    """
    cfg = {}

    patterns = {
        "host": r'COUCHBASE_HOST\s*=\s*["\']([^"\']+)["\']',
        "username": r'COUCHBASE_USERNAME\s*=\s*["\']([^"\']+)["\']',
        "password": r'COUCHBASE_PASSWORD\s*=\s*["\']([^"\']+)["\']',
        "bucket": r'COUCHBASE_BUCKET\s*=\s*["\']([^"\']+)["\']',
        "scope": r'COUCHBASE_SCOPE\s*=\s*["\']([^"\']+)["\']',
    }

    for key, pattern in patterns.items():
        m = re.search(pattern, code_str)
        if m:
            cfg[key] = m.group(1)

    # Build connectionString if host found
    if "host" in cfg and "connectionString" not in cfg:
        cfg["connectionString"] = f"couchbase://{cfg['host']}"

    return cfg



def main(spark_conf):
    try:
        spark = None
        if len(sys.argv) < 6:
            logger.info("Usage: spark-submit --master local[2] main.py <job_id> <user_id> <schedule_id> <run_id> <type>")
            sys.exit(1)
        job_id = sys.argv[1]
        user_id = sys.argv[2]
        schedule_id = sys.argv[3]
        run_id = sys.argv[4]
        executiontype = sys.argv[5]
        
        schedule_document = mongo_to_yaml.get_schedule_document(schedule_id)

        if ("meta_schedule_version" in schedule_document and schedule_document["meta_schedule_version"] == 2) or "export_files_list" in schedule_document:
            # For new schedules we fetch the updated pipeline or code from chat
            pipeline = ExportPipeline().export_pipeline(
                job_id,
                user_id,
                schedule_document.get("job_details"),
                mongo_to_yaml.get_chat_document(job_id),
                executiontype
            )
            yml = mongo_to_yaml.process_chat_pipeline(pipeline)
            code = mongo_to_yaml.get_code_from_chat(job_id)
        else:
            # For old schedules we fetch pipeline or code from schedule
            yml = mongo_to_yaml.process(schedule_id)
            code = mongo_to_yaml.get_code(schedule_id)

        schedule_conf={}
        schedule_conf["schedule_id"]=schedule_id
        schedule_conf["run_id"]= run_id
        schedule_conf["chat_id"] = job_id
        schedule_conf["user_id"] = user_id

        # Extract export_format from schedule document, default to 'csv' if not available
        if schedule_document.get('type') == 'localstorage':
            export_format = schedule_document.get("export_format", "csv")
            schedule_conf["export_format"] = export_format

        connection_id_dict = prepare_connection_id.process(schedule_id, user_id)
        connection_id_dict = replace_connections.process(connection_id_dict, schedule_id, user_id)
        config = configuration.get(schedule_id)

        if "--conf" in config:
            for key, value in config["--conf"].items():
                spark_conf = spark_conf.set(key, value)

        log_level = config.get("--conf",{}).get("spark.log.level", "INFO")
        spark_conf.set("spark.log.level", log_level)
        spark_conf.set("spark.sql.legacy.timeParserPolicy","LEGACY")

        # Apply connection-specific Spark configurations
        connection_spark_conf = _get_connection_specific_spark_conf(connection_id_dict)
        for key, value in connection_spark_conf.items():
            spark_conf.set(key, value)

        if executiontype == "code":
            cb_cfg = extract_couchbase_from_code(code)
            if cb_cfg.get("connectionString"):
                spark_conf.set("spark.couchbase.connectionString", cb_cfg["connectionString"])
            if cb_cfg.get("username"):
                spark_conf.set("spark.couchbase.username", cb_cfg["username"])
            if cb_cfg.get("password"):
                spark_conf.set("spark.couchbase.password", cb_cfg["password"])
            if cb_cfg.get("bucket"):
                spark_conf.set("spark.couchbase.implicitBucket", cb_cfg["bucket"])

            logger.info(f"Applied Couchbase configs from ACE code: {cb_cfg}")

        # Reuse existing SparkContext/SparkSession if present to avoid multiple-context errors
        spark = (
            SparkSession.builder
            .config(conf=spark_conf)
            .getOrCreate()
        )
        sc = spark.sparkContext
        sc.setLogLevel(log_level)
        set_logging_level(log_level)
        
        if executiontype == "code":
            schedule_conf["execution_type"] = "code"

            # Create spark engine instances using factory functions
            file_ops: SparkReadOrWriteFiles = create_file_operations("spark", user_id, localDirectory._path)
            df_ops: SparkDataframeInformation = create_dataframe_operations("spark",{})
            
            aod_audit_tracker: AuditTracker = AuditTracker(
                audit_runs_collection=mongo_audit_runs,
                audit_usage_collection=mongo_audit_usage,
                run_context=ScheduleRunContext(
                    user_id=user_id,
                    chat_id=job_id,
                    schedule_id=schedule_id,
                    run_id=run_id,
                    execution_type="code"
                )
            )
            
            aod_spark_context: AodSparkContext = AodSparkContext(
                spark_session=spark,
                audit_tracker=aod_audit_tracker
            )
            
            global_scope = {
                "Connection": Connection(connection_id_dict),
                "connection": connection_id_dict, 
                "JobArguments": JobArguments(config),
                "DataframeInformation": df_ops,     
                "ReadOrWriteFiles": file_ops,
                "CustomSparkContext": aod_spark_context,
                "AodAudit": aod_audit_tracker
            }
            wrapped_code = _wrap_custom_libraries(code)
            exec(wrapped_code, global_scope)
        elif executiontype == "pipeline":
            schedule_conf["execution_type"] = "pipeline"
            aod_audit_tracker: AuditTracker = AuditTracker(
                audit_runs_collection=mongo_audit_runs,
                audit_usage_collection=mongo_audit_usage,
                run_context=ScheduleRunContext(
                    user_id=user_id,
                    chat_id=job_id,
                    schedule_id=schedule_id,
                    run_id=run_id,
                    execution_type="pipeline"
                )
            )
            schedule_conf["AodAudit"] = aod_audit_tracker
            # remove 'source_name' keys from database type connections
            for key in connection_id_dict.keys():
                if connection_id_dict[key].get('type') == "database":
                    connection_id_dict[key].pop("source_name", None)
                if connection_id_dict[key].get('source_type') == "s3":
                    connection_id_dict[key].pop("source_name", None)
            pipeline = Manager(yaml.safe_load(yml), connection_id_dict, config, spark,schedule_conf)
            pipeline.manage()
        return True
    except Exception as e:
        logger.error(f"Failed to process the chat history: {str(e)}")
        raise MainException("Failed to process the yaml file..") from e
    finally:
        if spark is not None:
            spark.stop()


if __name__ == "__main__":
    spark_conf = SparkConf()
    logger.debug(spark_conf)
    main(spark_conf)