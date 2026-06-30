

from datetime import datetime
import uuid
from ....exceptions.exceptions import UtilityException
from ....logger.logger import Logger, logger
from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory

class ExportPipeline:
    """
    Class to handle export pipeline operations.

    Provides methods for exporting pipeline data and preparing schedule data for export.

    Attributes:
        session (Session): The MongoDB session used for transactions.

    Methods:
        export_pipeline(chat_id, user_id, details, chat_document, executionType):
            Exports the pipeline data based on the given parameters and updates the chat history.

        prepare_schedule_data(job_id, user_id, schedule_interval, advanced_scheduling, pipeline, config, schedule_name, code):
            Prepares the schedule data for export based on the given parameters.

    Exceptions:
        UtilityException: If an error occurs during the export process.
    """
    def _get_export_step_history_with_files_list(self, details, export_type):
        if export_type == "localstorage":
            history = {
                "id": str(uuid.uuid4()),
                "step": "export",
                "status": "PASS",
                "function": "export",
                "parameters": details.get("files_list")[0],
                "output":None
            }
        else:
            parameters = {
                "user_id": details["files_list"][0].get("user_id", ""),
                "chat_id": details["files_list"][0].get("chat_id", ""),
                "connection_id": details.get("connection_id", ""),
                "table_name": details.get("catalog", ""),
                "source_id": details["files_list"][0]["source_id"]
            }
            history = {
                "id": str(uuid.uuid4()),
                "step": "export",
                "status": "PASS",
                "function": "export_table",
                "parameters": parameters,
                "output":None
            }
        return history
    
    def _get_export_step_from_last_step(self, chat_history, chat_document, user_id, chat_id):
        if len(chat_history) > 0:
            history = {
                "id": str(uuid.uuid4()),
                "step": "export",
                "status": "PASS",
                "output": None
            }
            last_step = chat_history[-1]
            file_obj = self.get_file_object(
                chat_document.get('files'), last_step.get('parameters'))
            function_name = 'export'
            if last_step.get('function') == 'export':
                data = file_obj
                history["function"] = function_name
                history["parameters"] = data
            elif last_step.get('function') == 'export_table':
                data = last_step.get('parameters')
                data["user_id"] = user_id
                data["chat_id"] = chat_id
                data["source_id"] = file_obj.get("source_id", "")
                function_name = 'export_table'
                history["function"] = function_name
                history["parameters"] = data
            elif last_step.get('function') in ["read_files", "read_tables", "read", "filter_value", "union", "joins", "aggregate", "expression", "sql"]:
                data = self.get_file_object(chat_document.get('files'), last_step.get('output'))
                history["function"] = function_name
                history["parameters"] = data
            elif last_step.get('function') == "pytool":# TODO: Handle the delete case in the pytool.
                if last_step.get('output'): 
                    data = self.get_file_object(chat_document.get('files'), last_step.get('output')[-1])    
                    history["function"] = function_name
                    history["parameters"] = data
                else:
                    history = self._get_export_step_from_last_step(chat_history[:-1], chat_document, user_id, chat_id)
            else:
                data = file_obj
                history["function"] = function_name
                history["parameters"] = data
        else:
            history = {}
        
        if history == {}:
            raise RuntimeError("Unable to determine file to export automatically, please select one")
        return history
    
    @Logger.generate
    def export_pipeline(self, chat_id,user_id, details,chat_document, executionType):# pragma: no cover
        """
        Exports the pipeline data based on the given parameters.

        :param chat_id: The unique identifier for the chat.
        :type chat_id: str
        :param user_id: The unique identifier for the user.
        :type user_id: str
        :param details: The details of the export.
        :type details: dict
        :param chat_document: The document containing chat history.
        :type chat_document: dict
        :param executionType: The type of execution ('pipeline' or other).
        :type executionType: str
        :return: The updated chat history.
        :rtype: list
        :raises UtilityException: If an error occurs during the export process.
        """
        try:
            if executionType == "":
                executionType = "pipeline"
            if executionType == "pipeline" or executionType == "yaml":
                chat_history = chat_document.get("history", [])
                export_type = details.get("type", "localstorage") # If "type" not provided, default to "localstorage"
                
                if "files_list" in details and len(details["files_list"]) > 0:
                    # use the export file supplied in arguments
                    history = self._get_export_step_history_with_files_list(details, export_type)
                else:
                    # determine export file from last step
                    history = self._get_export_step_from_last_step(chat_history, chat_document, user_id, chat_id)
                
                step_export_exist = False
                chat_history = chat_document.get("history", [])
                for i, item in enumerate(chat_history):
                    if item.get("function") in ["export", "export_table"]:
                        chat_history[i] = history
                        step_export_exist = True
                        break
                if step_export_exist:
                    pass
                else:
                    if history:
                        chat_history.append(history)
                    chat_history = chat_document.get("history", [])
                
                return chat_history
            elif executionType == "code":
                logger.info("Export pipeline is not expected to anything for code execution mode")
                return chat_document.get("history", [])
            else:
                raise ValueError("Invalid executionType to export_pipeline")

        except Exception as e:
            logger.error(f"{e}", exc_info=True)
            raise UtilityException(e) from e

    def get_file_object(self, chat_files, parameters):
        if chat_files is None or chat_files == []:
            return {}
        for item in chat_files:
            if item.get("alias") == parameters.get("table_name") or item.get("alias") == parameters.get("file_name") or item.get("source_id") == parameters.get("source_id"):
                return item

    def prepare_schedule_data(
                self,job_id,user_id,schedule_interval,advanced_scheduling, pipeline, config,
                schedule_name,code,engine_type,generated_cron_expression,replace_connections=None, notification=None, 
                export_files_list=None, type='localstorage', execution_type='pipeline', job_details=None,export_format=None
            ):
            """
            Prepares the schedule data for export.

            :param job_id: The unique identifier for the job.
            :type job_id: str
            :param user_id: The unique identifier for the user.
            :type user_id: str
            :param schedule_interval: The schedule interval in cron format.
            :type schedule_interval: str
            :param advanced_scheduling: The advanced scheduling parameters.
            :type advanced_scheduling: dict
            :param pipeline: The pipeline data.
            :type pipeline: list
            :param config: The configuration details.
            :type config: dict
            :param schedule_name: The name of the schedule.
            :type schedule_name: str
            :param code: The code associated with the schedule.
            :type code: str
            :return: The prepared schedule data.
            :rtype: dict
            """
            data = {
                "chat_id":job_id,
                "user_id":user_id,
                "schedule_name":schedule_name,
                "engine_type":engine_type,
                "schedule_interval" : schedule_interval,
                "generated_cron_expression":generated_cron_expression,
                "advanced_scheduling" :advanced_scheduling,
                "pipeline":pipeline,
                "configurations":config,
                "code":code,
                "replace_connections":replace_connections if replace_connections is not None else {},
                "notification":notification if notification is not None else {},
                "export_files_list": export_files_list if export_files_list is not None else [],
                "type": type,
                "execution_type": execution_type,
                "job_details": job_details if job_details is not None else {},
                "export_format": export_format
            }
            return data
class NotificationUtils:
    def __init__(self, session=None):# pragma: no cover
        """
        Initialize the AirflowAPI with the Airflow URL and credentials.
        """
        self.session = session
        self.mongo_connector = MongoConnector()
        self.mongo_client = self.mongo_connector.client
        self.users_collection = MongoFactory(self.mongo_client, "users", session=self.session)
    @Logger.generate
    def get_notification_details(self, user_id, notification):
        """
        Retrieves and updates the notification details for a given user and 
        notification. This function is designed to ensure that the notification 
        details include necessary information, such as the recipient's email address 
        and the subject for email notifications.

        :param user_id: The ID of the user for whom the notification details are 
            being retrieved.
        :type user_id: str
        :param notification: A dictionary containing the notification details, 
            including the type and specific details such as email 'to' address 
            and 'subject'.
        :type notification: dict
        :return: The updated notification dictionary with complete details.
        :rtype: dict
        """
        notification_type = notification.get("type")
        if notification_type == "email":
            notification_details = notification.get("details", {})
            if not notification_details.get("to"):
                notification_details['to'] = self.users_collection.get_by_id(user_id)[1].get("email")
            notification['details'] = notification_details

        return notification 

    

class RestTriggerUtils:
    """
    Utility class for generating cron expressions and other scheduling-related functionalities.
    """

    def generate_cron(self,repeats, repeats_every, days_of_week, repeat_by, day_of_month=False, day_of_week=False):
        """
        Generates a cron expression based on the provided scheduling parameters.

        :param repeats: The frequency of the repetition (minutely, hourly, daily, weekly, monthly, yearly).
        :type repeats: str
        :param repeats_every: The interval for the repetition.
        :type repeats_every: int
        :param days_of_week: List of days of the week for weekly repetitions.
        :type days_of_week: list
        :param repeat_by: The repeat criteria (day_of_month or day_of_week).
        :type repeat_by: str
        :param day_of_month: Flag indicating if the repeat is by day of the month, defaults to False.
        :type day_of_month: bool, optional
        :param day_of_week: Flag indicating if the repeat is by day of the week, defaults to False.
        :type day_of_week: bool, optional
        :return: The generated cron expression.
        :rtype: str
        :raises ValueError: If the repeat interval or format is invalid.
        """
        if repeats == "minutely":
            return f"*/{repeats_every} * * * *"
        elif repeats == "hourly":
            return f"0 */{repeats_every} * * *"
        elif repeats == "daily":
            return f"0 0 */{repeats_every} * *"
        elif repeats == "weekly":
            if days_of_week:
                days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                days_str = ",".join(str(days.index(day)) for day in days_of_week)
                return f"0 0 * * {days_str}"
            else:
                return f"0 0 * * 0"  # Sunday as the default
        elif repeats == "monthly":
            if day_of_month:
                try:
                    date = datetime.strptime(repeat_by, "%Y-%m-%d")
                    day_of_month = date.day
                    return f"0 0 {day_of_month} */{repeats_every} *"
                except ValueError:
                    raise ValueError("Invalid date format for repeat_by. It must be in the format 'dd-mm-yyyy'.")
            elif day_of_week:
                try:
                    date = datetime.strptime(repeat_by, "%Y-%m-%d")
                    week_of_month = RestTriggerUtils().get_week_of_month(date)
                    day_of_week =  RestTriggerUtils().get_day_of_week(date)
                    return f"0 0 * * {day_of_week}#{week_of_month}"
                except ValueError:
                    raise ValueError("Invalid format for repeat_by. It must be in the format 'week_of_month day_of_week' (e.g., '2 3').")  
            else:
                raise ValueError("Invalid repeat_by_format. It must be either 'day_of_month' or 'day_of_week'.")
        elif repeats == "yearly":
            return f"0 0 1 1 */{repeats_every}"
        else:
            raise ValueError("Invalid repeat interval")
        

    def get_week_of_month(self, date):
        """
        Calculates the week of the month for a given date.

        :param date: The date to calculate the week of the month.
        :type date: datetime
        :return: The week of the month.
        :rtype: int
        """
        # Find the first day of the month
        first_day = date.replace(day=1)
        # Calculate the day of the week for the first day of the month (0=Monday, 6=Sunday)
        first_day_weekday = first_day.weekday()
        # Calculate the week number
        if first_day_weekday == 6:
            # If the first day is Sunday, then the first week starts from day 1 to day 7
            week_number = (date.day - 1) // 7 + 1
        else:
            # Calculate the week number based on the first day of the month
            week_number = (date.day + first_day_weekday - 1) // 7 + 1
        return week_number

    def get_day_of_week(self, date):
        """
        Calculates the day of the week for a given date.

        :param date: The date to calculate the day of the week.
        :type date: datetime
        :return: The day of the week as an integer (0=Sunday, 6=Saturday).
        :rtype: int
        """
        # Define a list of day names
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        # Get the weekday number (0=Sunday, 6=Saturday)
        day_index = date.strftime("%A")  
        # Return the corresponding day index
        return days.index(day_index)
    
class PackageUtils:
    def get_package(self, type, subtype=""):
        packages = {
            "system": ["org.apache.commons:commons-dbcp2:2.8.0","org.apache.iceberg:iceberg-spark-runtime-3.3_2.12:1.4.2","io.delta:delta-core_2.12:2.2.0"],
            "datasource": {
                "csv": "",
                "xlsx": "com.crealytics:spark-excel_2.12:0.13.5",
                "astra": "com.datastax.spark:spark-cassandra-connector_2.12:3.3.0",
                "cassandra": "com.datastax.spark:spark-cassandra-connector_2.12:3.3.0",
                "firebird": "org.firebirdsql.jdbc:jaybird:5.0.4.java11",
                "mysql": "mysql:mysql-connector-java:8.0.13",
                "postgres": "org.postgresql:postgresql:42.7.1",
                "redshift": "com.amazon.redshift:redshift-jdbc42:2.1.0.26",
                "snowflake": "net.snowflake:snowflake-jdbc:3.13.30,net.snowflake:spark-snowflake_2.12:2.12.0-spark_3.3",
                "oracle": "com.oracle.database.jdbc:ojdbc8:19.8.0.0",
                "s3": "org.apache.hadoop:hadoop-aws:3.3.3,com.amazonaws:aws-java-sdk-bundle:1.12.262",
                "couchbase-spark-connector": "com.couchbase.client:spark-connector_2.12:3.3.6",
                "databricks-jdbc": "com.databricks:databricks-jdbc:2.7.3",
            }
        }
        if subtype:
            return packages.get(type, {}).get(subtype)
        return packages.get(type)


class DLTPackageUtils:
    """
    Utility class for managing DLT packages (pip packages and DLT extras)
    This is where ALL DLT datasource to package mapping is defined
    """
    
    def get_dlt_package(self, type, subtype=""):
        """
        Get DLT packages (pip packages and DLT extras)
        Optimized based on requirements.txt - only returns packages NOT in base image
        
        :param type: Package type ('datasource' or 'system')
        :param subtype: Datasource subtype (e.g., 'mysql', 'postgres', 's3')
        :return: Comma-separated package string or empty string
        
        Examples:
            get_dlt_package("datasource", "postgres") -> "" (already in base)
            get_dlt_package("datasource", "mysql") -> "" (already in base)
            get_dlt_package("datasource", "bigquery") -> "dlt[bigquery]"
            get_dlt_package("datasource", "s3") -> "dlt[s3]"
        """
        packages = {
            "system": [],  # No system packages needed - already in base DLT image
            
            "datasource": {
                # ===== File Formats (Already in Base Image) =====
                "csv": "",  # pandas (already in base)
                "json": "",  # stdlib (already in base)
                
                # ===== SQL Databases (Already in Base Image) =====
                "postgres": "",  # dlt[postgres] + psycopg2-binary==2.9.9 (already in base) dlt[postgres]>=1.14.0
                "postgresql": "",  # Alias for postgres
                "snowflake": "snowflake-sqlalchemy",  # dlt[snowflake] (already in base)
                "mysql": "",  # mysql-connector-python==8.4.0 (already in base)
                "couchbase": "",  # couchbase==4.3.6 (already in base)
                
                # ===== SQL Databases (Need Installation) =====
                "redshift": "dlt[redshift]>=1.14.0",
                "bigquery": "dlt[bigquery]>=1.14.0",
                "databricks": "dlt[databricks]>=1.14.0,databricks-sql-connector==4.0.5,databricks-sqlalchemy==2.0.7",
                "mssql": "dlt[mssql]>=1.14.0",
                "sqlserver": "dlt[mssql]>=1.14.0",  # Alias
                "oracle": "dlt[oracle]>=1.14.0",
                
                # ===== NoSQL Databases (Need Installation) =====
                "cassandra": "dlt[cassandra]>=1.14.0",
                "astra": "dlt[cassandra]>=1.14.0",  # DataStax Astra uses Cassandra
                
                # ===== Cloud Storage (Need Installation) =====
                "s3": "",  # AWS S3 (Already in Base Image)
                
                # ===== Additional Drivers =====
                "firebird": "fdb>=2.0.0",  # Firebird Python driver
            }
        }
        
        if subtype:
            return packages.get(type, {}).get(subtype, "")
        return packages.get(type, [])