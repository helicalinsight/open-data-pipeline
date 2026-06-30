from configparser import NoSectionError
import json
import logging
import ast
import uuid
import requests
import base64
import time
import codecs
from typing import Optional, Mapping
from datetime import datetime
import pytz
from urllib.parse import quote, urlencode
from collections import defaultdict
from itertools import chain

import ast
import os
import sys
from enum import Enum
from flask import Response

from .engine_interface import get_engine

from ....configurations.api.config import Config, BaseConfig
    
from ....logger.logger import logger, Logger

from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from .utils import DLTPackageUtils, ExportPipeline, NotificationUtils, PackageUtils
from src.api.services.base.service_parent import ServiceParent
# Enhanced Logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RequestType(Enum):
    """
    Enum class for HTTP request types used in API calls.

    Attributes:
        GET (str): Represents the HTTP GET request method.
        POST (str): Represents the HTTP POST request method.
        DELETE (str): Represents the HTTP DELETE request method.
        PUT (str): Represents the HTTP PUT request method.
        PATCH (str): Represents the HTTP PATCH request method.
    """
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"
    PATCH = "PATCH"

class AirflowAPI(ServiceParent):
    """
    Class to handle interactions with Airflow's REST API.

    This class provides methods to encode credentials, make API calls, and interact with Airflow's server.

    Attributes:
        airflow_url (str): The URL of the Airflow server.
        username (str): The username for authenticating with the Airflow server.
        password (str): The password for authenticating with the Airflow server.
        session (object, optional): An optional session parameter for database connections.
        mongo_connector (MongoConnector): MongoDB connector instance.
        mongo_client (MongoClient): MongoDB client instance.
        schedule_collection (MongoFactory): MongoDB collection instance for schedules.
        chats_collection (MongoFactory): MongoDB collection instance for chats.

    Methods:
        encode_credentials():
            Encodes the username and password into a format suitable for HTTP headers.

        call_api(request_type, endpoint, payload=None, expect_json=True):
            Makes an API call to the Airflow server.

    Exceptions:
        json.JSONDecodeError: If JSON decoding fails during the API response handling.
        requests.exceptions.RequestException: For general HTTP request errors.
    """

    def __init__(self, session=None):
        """
        Initialize the AirflowAPI with the Airflow URL and credentials.

        :param session: An optional session parameter for database connections.
        :type session: object, optional
        """
        self.airflow_url = Config.config["airflow"]["url"]
        self.username = Config.config["airflow"]["username"]
        self.password = Config.config["airflow"]["password"]
        self.config = Config.config
        self.dag_path = BaseConfig.DAGS_PATH
        super().__init__(session)
        self.schedule_collection = MongoFactory(self.client, "schedule", session=self.session)
        self.chats_collection = MongoFactory(self.client, "chats", session=self.session)
        self.users_collection = MongoFactory(self.client, "users", session=self.session)
        self.connections_collection = MongoFactory(self.client, "connections", session=self.session)
        self.files_collection = MongoFactory(self.client, "files", session=self.session)
        self.dms_schedule_progress_collection = MongoFactory(self.client, "dms_schedule_progress", session=self.session)


    @Logger.generate
    def encode_credentials(self):
        """
        Encodes the username and password into a format suitable for HTTP headers.

        :return: The encoded credentials.
        :rtype: str
        """

        credentials = f'{self.username}:{self.password}'
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        logger.info("Returning encoded credentials")
        return encoded_credentials

    @Logger.generate
    def _generate_cron(self, repeats, repeats_every, days_of_week, repeat_by, start_time, day_of_month=False, day_of_week=False):
        """
        Generate a cron expression based on scheduling parameters.
        
        :param repeats: Frequency type (minutely, hourly, daily, weekly, monthly, yearly)
        :param repeats_every: Interval for repetition
        :param days_of_week: List of days for weekly scheduling
        :param repeat_by: Reference date for monthly scheduling
        :param start_time: Start time object
        :param day_of_month: Boolean for monthly by day of month
        :param day_of_week: Boolean for monthly by day of week
        :return: Cron expression string
        """
        # Parse start_time into hour and minute
        try:
            start_time_str = start_time.strftime("%H:%M")
            start_time_obj = datetime.strptime(start_time_str, "%H:%M")
            start_hour = start_time_obj.hour
            start_minute = start_time_obj.minute
        except ValueError:
            raise ValueError("Invalid start_time format. It must be in the format 'HH:MM'.")

        if repeats == "minutely":
            return f"*/{repeats_every} * * * *"
        elif repeats == "hourly":
            return f"{start_minute} */{repeats_every} * * *"
        elif repeats == "daily":
            return f"{start_minute} {start_hour} */{repeats_every} * *"
        elif repeats == "weekly":
            if days_of_week:
                days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                days_str = ",".join(str(days.index(day)) for day in days_of_week)
                return f"{start_minute} {start_hour} * * {days_str}"
            else:
                return f"{start_minute} {start_hour} * * 0"  # Default to Sunday
        elif repeats == "monthly":
            if day_of_month:
                try:
                    date = datetime.strptime(repeat_by, "%Y-%m-%d")
                    day_of_month = date.day
                    return f"{start_minute} {start_hour} {day_of_month} */{repeats_every} *"
                except ValueError:
                    raise ValueError("Invalid date format for repeat_by. It must be in the format 'YYYY-MM-DD'.")
            elif day_of_week:
                try:
                    date = datetime.strptime(repeat_by, "%Y-%m-%d")
                    week_of_month = self._get_week_of_month(date)
                    day_of_week = self._get_day_of_week(date)
                    return f"{start_minute} {start_hour} * * {day_of_week}#{week_of_month}"
                except ValueError:
                    raise ValueError("Invalid format for repeat_by. It must be in the format 'week_of_month day_of_week' (e.g., '2 3').")
            else:
                raise ValueError("Invalid repeat_by format. It must be either 'day_of_month' or 'day_of_week'.")
        elif repeats == "yearly":
            return f"{start_minute} {start_hour} 1 1 */{repeats_every}"
        else:
            raise ValueError("Invalid repeat interval")

    @Logger.generate
    def _get_week_of_month(self, date):
        """
        Calculate which week of the month a given date falls into.
        
        :param date: Date object
        :return: Week number (1-5)
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

    @Logger.generate
    def _get_day_of_week(self, date):
        """
        Get the day of week index for a given date.
        
        :param date: Date object
        :return: Day index (0=Sunday, 6=Saturday)
        """
        # Define a list of day names
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        # Get the weekday number (0=Sunday, 6=Saturday)
        day_index = date.strftime("%A")
        
        # Return the corresponding day index
        return days.index(day_index)

    @Logger.generate
    def _generate_cron_expression(self, schedule_interval, advanced_scheduling):
        """
        Generate cron expression based on schedule interval and advanced scheduling.
        This is moved from rest-trigger-dag to eliminate lag.
        
        :param schedule_interval: Basic schedule interval
        :param advanced_scheduling: Advanced scheduling parameters
        :return: Generated cron expression
        """
        try:
            # Handle basic schedule intervals first
            if not advanced_scheduling:
                if schedule_interval and schedule_interval != "once":
                    return f'@{schedule_interval}'
                return None
            
            # Extract advanced scheduling parameters
            frequency = advanced_scheduling.get("Frequency")
            repeats_every = advanced_scheduling.get("RepeatsEvery")
            days_of_week = advanced_scheduling.get("DaysofWeek") if frequency == "weekly" and repeats_every == 1 else None
            repeat_by = advanced_scheduling.get("RepeatBy")
            
            # Parse start time
            start_time_str = advanced_scheduling.get("StartTime", "00:00:00")
            start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
            
            # Handle monthly scheduling specifics
            day_of_the_month = False
            day_of_the_week = False
            if frequency == "monthly":
                day_of_the_month = repeat_by == "dayOfTheMonth"
                day_of_the_week = repeat_by == "dayOfTheWeek"
                repeat_by = advanced_scheduling.get("StartDate")  # Use StartDate for repeat_by in monthly
            
            # Generate cron expression using utility
            if frequency:
                cron_expression = self._generate_cron(
                    frequency,
                    repeats_every,
                    days_of_week,
                    repeat_by,
                    start_time,
                    day_of_the_month,
                    day_of_the_week
                )
                logger.info(f"Generated cron expression: {cron_expression}")
                return cron_expression
            
            # Fallback to basic schedule interval
            if schedule_interval and schedule_interval != "once":
                return f'@{schedule_interval}'
                
            return None
            
        except Exception as e:
            logger.error(f"Error generating cron expression: {str(e)}")
            # Fallback to basic schedule interval
            if schedule_interval and schedule_interval != "once":
                return f'@{schedule_interval}'
            return None

    @Logger.generate
    def call_api(self, request_type, endpoint, payload=None, expect_json=True): # pragma: no cover
        """
        Makes an API call to the Airflow server.

        :param request_type: The type of HTTP request (GET, POST, DELETE).
        :type request_type: str
        :param endpoint: The endpoint URL to which the request will be made.
        :type endpoint: str
        :param payload: Data payload for POST requests, defaults to None.
        :type payload: dict, optional
        :param expect_json: A flag indicating whether a JSON response is expected, defaults to True.
        :type expect_json: bool, optional
        :return: The response from the API call.
        :rtype: dict or str
        """
        headers = {
            'Authorization': f'Basic {self.encode_credentials()}',
            'Content-Type': 'application/json'
        }
        if expect_json:
            headers['Accept'] = 'application/json'
        url = f"http://{self.airflow_url}{endpoint}"
        try:
            if request_type.value=='DELETE':
                headers = {
                'Authorization': f'Basic {self.encode_credentials()}',
                'Accept': '*/*'}
            response = requests.request(method=request_type.value, url=url, headers=headers, json=payload)
            if response.status_code >= 400:
                logger.error(f"API request failed: {response.text}", exc_info=True)
                return {"error": response.text, "status_code": response.status_code}

            if not expect_json:
                return response.text
            if response.status_code in [204, 205]:
                return {}
            
            return response.json()
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding failed: {str(e)}", exc_info=True)
            return {"error": "Failed to decode JSON", "response": response.text, "status_code": response.status_code}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}", exc_info=True)
            return {"error": str(e), "status_code": 500}
        
    def is_valid_execution_type(self, execution_type: Optional[str]) -> bool:
        if execution_type is None:
            return True
        
        return execution_type in ['pipeline', 'code', 'yaml']

    def is_valid_engine_type(self, engine_type: Optional[str]) -> bool:
        if engine_type is None:
            return True
        # Supported engines for scheduling path
        return engine_type in ['spark', 'dlt']

    @Logger.generate
    def dag_exists(self, job_id):
        """
        Check if a DAG (Directed Acyclic Graph) exists.

        :param job_id: The ID of the DAG to check.
        :type job_id: str
        :return: True if the DAG exists, False otherwise.
        :rtype: bool
        """
        response = self.call_api(RequestType.GET, f"/api/v1/dags/{job_id}")
        return 'error' not in response

    def _packages(self, configurations, pipeline, user_id, replace_connections = {}):
        user_packages = configurations.get("--packages","")
        system_packages = PackageUtils().get_package("system")
        datasource_packages = []
        for connection in replace_connections.values():
            conn_type = connection.get("connectionType")
            datasource_packages.append(PackageUtils().get_package("datasource", conn_type))
        for step in pipeline:
            if step['function'] == "read_files":
                file_id = step['parameters']['file_id']
                _, files = self.files_collection.get_all_by_user_id(user_id)
                for document in files:
                    for file in document["files"]:
                        if file['file_id'] == file_id:
                            if file["file_type"] ==".csv":
                                pass
                            if file["file_type"] ==".xlsx":
                                datasource_packages.append(PackageUtils().get_package("datasource", "xlsx"))
            elif step['function'] == "read_tables":
                conn_id = step['parameters']['connection_id']
                _, conn = self.connections_collection.get_by_id(conn_id)
                conn_type = conn.get("type", "")
                datasource_packages.append(PackageUtils().get_package("datasource", conn_type))
            elif step['function'] == "read":
                conn_id = step['parameters']['connection_id']
                _, conn = self.connections_collection.get_by_id(conn_id)
                conn_type = conn.get("type", "")
                datasource_packages.append(PackageUtils().get_package("datasource", conn_type))
                file_type = step["parameters"]["type"]
                datasource_packages.append(PackageUtils().get_package("datasource", file_type))
        dependencies = [system_packages,user_packages,datasource_packages]
        packages = ",".join(
            dep for item in dependencies
            for dep in (item if isinstance(item, list) else [item])
            if dep
        )
        packages = ",".join(dict.fromkeys(packages.split(','))) # removing duplicates
        return packages
    
    
    def _dlt_packages(self, configurations, pipeline, user_id):
        """
        Get DLT packages (pip packages) based on pipeline
        
        :param configurations: Configuration dict with --packages
        :param pipeline: Pipeline steps list
        :param user_id: User ID
        :return: Comma-separated DLT package string
        """
        # User-defined packages from --packages configuration
        user_packages = configurations.get("--packages", "")
        
        # No system packages for DLT (already in base image)
        datasource_packages = []
        
        # Iterate through pipeline to detect datasources
        for step in pipeline:
            if step['function'] == "read_files":
                # Detect file types from uploaded files
                file_id = step['parameters'].get('file_id')
                if file_id:
                    _, files = self.files_collection.get_all_by_user_id(user_id)
                    for document in files:
                        for file in document.get("files", []):
                            if file.get('file_id') == file_id:
                                file_type = file.get("file_type", "").lower().lstrip('.')
                                
                                if file_type in ["xlsx", "xls"]:
                                    pkg = DLTPackageUtils().get_dlt_package("datasource", file_type)
                                    if pkg:
                                        datasource_packages.append(pkg)
                                # csv and json are already in base image, skip
                                
            elif step['function'] == "read_tables":
                # Detect database type from connection
                conn_id = step['parameters'].get('connection_id')
                if conn_id:
                    _, conn = self.connections_collection.get_by_id(conn_id)
                    conn_type = conn.get("type", "").lower()
                    pkg = DLTPackageUtils().get_dlt_package("datasource", conn_type)
                    if pkg:
                        datasource_packages.append(pkg)

            elif step['function'] == "data_migration":
                # Handle DMS related package loading
                try:
                    for conn_source in ('source_parameters', 'destination_parameters'):
                        conn = None
                        if conn_source in step:
                            if step[conn_source].get('connection_id'):
                                conn_id = step[conn_source]['connection_id']
                                _, conn = self.connections_collection.get_by_id(conn_id)
                        
                        if conn and isinstance(conn, dict):
                            conn_type = conn.get("type", "").lower()
                            pkg = DLTPackageUtils().get_dlt_package("datasource", conn_type)
                            if pkg:
                                datasource_packages.append(pkg)
                except KeyError as e:
                    logger.error(f"Error getting package for connection {conn_id}: {e}")

            elif step['function'] == "read":
                # Detect both connection type and file type
                conn_id = step['parameters'].get('connection_id')
                if conn_id:
                    _, conn = self.connections_collection.get_by_id(conn_id)
                    conn_type = conn.get("type", "").lower()
                    pkg = DLTPackageUtils().get_dlt_package("datasource", conn_type)
                    if pkg:
                        datasource_packages.append(pkg)
                
                # Check for file type in parameters
                file_type = step["parameters"].get("type", "").lower()
                if file_type:
                    pkg = DLTPackageUtils().get_dlt_package("datasource", file_type)
                    if pkg:
                        datasource_packages.append(pkg)
        
        # Combine all packages: user_packages + datasource_packages
        dependencies = [user_packages, datasource_packages]
        packages = ",".join(
            dep for item in dependencies
            for dep in (item if isinstance(item, list) else [item])
            if dep
        )
        
        # Remove duplicates while preserving order
        packages = ",".join(dict.fromkeys(packages.split(',')))
        
        logger.info(f"DLT packages detected: {packages}")
        return packages


    def _convert_packages_format(self, packages_str):
        """
        Convert package string format based on engine type.
        For DLT: Convert to space-separated format for pip
        
        :param packages_str: Comma-separated package string
        :type packages_str: str
        :return: Formatted package string
        :rtype: str
        """
        if not packages_str or not packages_str.strip():
            return ""
        # Convert comma-separated to space-separated for pip
        # Example: "redis==5.0.1,boto3==1.28.85" -> "redis==5.0.1 boto3==1.28.85"
        packages_list = [pkg.strip() for pkg in packages_str.split(',') if pkg.strip()]
        return ' '.join(packages_list)


    @Logger.generate
    def create_dag(
            self, job_id, user_id, job_name, schedule_interval, advanced_scheduling,
            job_details, schedule_name, executionType, run_engine_type,
            replace_connections=None, notification=None, should_create_v1_schedule=False,export_format=None
        ):
        
        """
        Create a DAG (Directed Acyclic Graph) with the provided job_id and user_id, and optionally set a schedule interval.

        :param job_id: The unique identifier for the DAG.
        :type job_id: str
        :param user_id: The ID of the user who owns the DAG.
        :type user_id: str
        :param job_name: The name of the job.
        :type job_name: str
        :param schedule_interval: Optional. The schedule interval for the DAG, in cron format.
        :type schedule_interval: str, optional
        :param advanced_scheduling: Advanced scheduling parameters.
        :type advanced_scheduling: dict
        :param job_details: Details about the job.
        :type job_details: dict
        :param schedule_name: The name of the schedule.
        :type schedule_name: str
        :param executionType: The type of execution (e.g., 'code', 'localstorage').
        :type executionType: str
        :return: A response indicating the success or failure of DAG creation.
        :rtype: tuple
        """
        try:
            if replace_connections is None:
                replace_connections = {}

            if notification is None:
                notification = {}     
            if self.dag_exists(job_id):
                logger.info(f"DAG with job_id: {job_id} already exists")
                return {"message": f"DAG with job_id: {job_id} already exists"}, 400
            if notification.get("active"):
                notification = NotificationUtils(session=self.session).get_notification_details(user_id, notification)
        
            if not self.is_valid_engine_type(run_engine_type):
                raise ValueError(f"Invalid engine_type {run_engine_type} passed, valid values are `spark` or `dlt`")
            engine = get_engine(run_engine_type)
            engine_type = engine.engine_type().value
        
            logger.info(f"Creating DAG for job {job_id} with engine type: {engine_type}")

            # Generate cron expression
            generated_cron_expression = self._generate_cron_expression(schedule_interval, advanced_scheduling)
            logger.info(f"Generated cron expression : {generated_cron_expression}")

            dag_data = {"conf": {"job_id": job_id, "user_id": user_id,"job_name":job_name}}
            dag_data["conf"]["schedule_interval"] = schedule_interval
            dag_data["conf"]["advanced_scheduling"] = advanced_scheduling
            dag_data['conf']['helper_module']=Config.config["airflow"]["helper_module"]
            dag_data['conf']["executionType"] = executionType # executionType can be "pipeline" / "yaml" / "code"
            dag_data['conf']["engine_type"] = engine_type #  Add engine type to dag_data
            dag_data['conf']['spark_path'] = Config.config["airflow"]["spark_path"]
            dag_data['conf']["service_type"] = "dts"  # Regular DAGs are DTS (Data Tranformation Service)

            status, chat_document=self.chats_collection.get_by_id(job_id)
            configurations=chat_document.get("configurations",{})
            if not self.is_valid_execution_type(executionType):
                raise ValueError(f"Invalid execution_type {executionType} passed, valid values are `pipeline`, `yaml` or `code`")
            if (executionType in {"pipeline", "yaml"} and chat_document.get("history")) or executionType == "code" or type == "code":
                code=chat_document.get("code",'')
                
                if job_details.get("type") is None:
                    job_details["type"] = "localstorage"
                    export_format = "csv" # default when no destination selected

                type = job_details.get("type", "localstorage") # If "type" parameter not provided, default to "localstorage"
                type = True if type == "localstorage" else False
                if executionType=='code':
                    pipeline = ExportPipeline().export_pipeline(job_id,user_id,job_details,chat_document,executionType)
                else:
                    pipeline = ExportPipeline().export_pipeline(job_id,user_id,job_details,chat_document,executionType)
                dag_data['conf']['local']=type


                if engine_type == "dlt":
                    # Use NEW DLT package function
                    dlt_packages_comma = self._dlt_packages(configurations, pipeline, user_id)
                    dlt_packages_space = self._convert_packages_format(dlt_packages_comma)
                    dag_data['conf']["pip_packages"] = dlt_packages_space
                    
                    logger.info(f"DLT packages (comma-separated): {dlt_packages_comma}")
                    logger.info(f"DLT packages (space-separated for pip): {dlt_packages_space}")
                    
                    dlt_conf = configurations.get("--conf", None)
                    dag_data['conf']["dlt_conf"] = dlt_conf
                    
                else:
                    spark_conf=configurations.get("--conf",None)
                    dag_data['conf']["spark_conf"]=spark_conf
                    dag_data['conf']['spark_path'] = Config.config["airflow"]["spark_path"]
                
                data = ExportPipeline().prepare_schedule_data(
                    job_id,
                    user_id,
                    schedule_interval,
                    advanced_scheduling,
                    pipeline,
                    configurations,
                    schedule_name,
                    code,
                    engine_type,
                    generated_cron_expression,
                    replace_connections=replace_connections,
                    notification=notification,
                    export_files_list=job_details.get("files_list", []),
                    type=job_details.get("type", "localstorage"),
                    execution_type=executionType,
                    job_details=job_details,
                    export_format=export_format
                )
                
                packages = self._packages(configurations, pipeline, user_id, replace_connections)

                if should_create_v1_schedule:
                    # remove new fields from data
                    data.pop("engine_type", None)
                    data.pop("type", None)
                    data.pop("execution_type", None)
                    data.pop("job_details", None)
                    data.pop("export_files_list", None)
                    data["meta_schedule_version"] = 1
                else:
                    data["meta_schedule_version"] = 2
                
                status, schedule_id = self.schedule_collection.insert_document(data)
                dag_data["conf"]["schedule_id"] = str(schedule_id)
                dag_data["conf"]["schedule_name"] = str(schedule_name)
                dag_data['conf']["notification"] = notification
                dag_data["conf"]["spark_packages"] = packages
                
                # Pass the generated cron expression to the DAG
                if generated_cron_expression:
                    dag_data["conf"]["generated_cron_expression"] = generated_cron_expression
                
                if schedule_interval == "once" or schedule_interval is None:
                    # This condition satisfies when create_dag is called from "Run Now" button
                    logger.info(f"Triggering run now for jobid - {job_id}, userid - {user_id}")
                    run_now_data = {
                        "conf": {
                            "job_id": job_id,
                            "user_id": user_id,
                            "spark_path": dag_data["conf"]["spark_path"],
                            "spark_packages": dag_data["conf"]["spark_packages"],
                            "execution_type": executionType,
                            "helper_module": dag_data["conf"]["helper_module"],
                            "schedule_id": dag_data["conf"]["schedule_id"],
                            "engine_type": engine_type, # NEW: Add engine type
                            "pip_packages": dag_data["conf"].get("pip_packages", "")
                        }
                    }
                    response = self.call_api(RequestType.POST, "/api/v1/dags/run_now_dag/dagRuns", run_now_data)
                else:
                    logger.info(f"Triggering schedule for jobid - {job_id}, userid - {user_id}")
                    # This condition satisfies when create_dag is called from "Schedule" button
                    response = self.call_api(RequestType.POST, "/api/v1/dags/rest-trigger/dagRuns", dag_data)
                
                if 'error' in response:
                    logger.debug("error in response")
                    return response, 500

                logger.info(f"Successfully generated DAG: {job_id} using job_id: {job_id}")
                return {
                    "message": f"Scheduled {schedule_name} schedule for the job {job_name} successfully",
                    "job_id": str(job_id),
                    "run_id": str(response["dag_run_id"]),
                    "local": dag_data['conf']['local'],
                    "schedule_id": dag_data["conf"]["schedule_id"],
                    "engine_type": engine_type, #Add engine type to response
                    "cron_expression": generated_cron_expression  # Return cron expression 
                }, 200
            else:
                return {
                    "message": "Cannot schedule on empty history.",
                    "job_id": None,
                    "run_id": None,
                    "local": None,
                    "schedule_id": None,
                    "engine_type": engine_type
                }, 200
        except Exception as e: # pragma: no cover
            raise Exception(e) from e
    
    def _create_and_return_dms_chat_document(self, migration_details, user_id, schedule_name):
        # TODO: Refactor to handle chat update using ChatService
        _, chat_id = self.chats_collection.insert_document(
            {
                "user_id": user_id,
                "chat_name": f"{schedule_name}_dms_chat",
                "job_mode": "llm",
                "history" : [migration_details],
                "service_mode": "DMS"
            }
        )
        _, chat_doc = self.chats_collection.get_by_id(chat_id)
        return chat_doc

    def _update_dms_chat_document(self, chat_id, migration_details, user_id, schedule_name):
        _, chat_doc = self.chats_collection.get_by_id(chat_id)
        # Remove any existing data_migration steps before appending the new one
        filtered_history = [item for item in chat_doc.get("history", []) if item.get("function") != "data_migration"]
        chat_doc["history"] = filtered_history + [migration_details]
        status, _ = self.chats_collection.update_one(_id=chat_id, key="history", data=chat_doc.get("history", []))
        if status is False:
            logger.error(f"Failed to update DMS chat {chat_id} in database with migration details")
        return chat_doc
        
    @Logger.generate
    def create_dms_dag(
            self, user_id, chat_id: str, schedule_name: str, schedule_interval, advanced_scheduling: dict, engine_type: str, execution_type: str, migration_details: dict, notification: dict = None):
        try:
            # Get notification details
            if notification is None:
                notification = {}
            
            if notification.get("active"):
                notification = NotificationUtils(session=self.session).get_notification_details(user_id, notification)
                
            generated_cron_expression = self._generate_cron_expression(schedule_interval, advanced_scheduling)
            
            dag_data = {
                "conf": {
                    "user_id": user_id,
                    "job_name": schedule_name,
                    "schedule_interval": schedule_interval,
                    "advanced_scheduling": advanced_scheduling,
                    "helper_module": Config.config["airflow"]["helper_module"],
                    "executionType": execution_type,
                    "engine_type": engine_type,
                    "service_type": "dms"  # DMS DAGs are tagged as "dms"
                }
            }
                
            
            # We need to create corresponding chat document with given details for DMS pipeline
            if chat_id is None:
                chat_doc = self._create_and_return_dms_chat_document(migration_details, user_id, schedule_name)
            else:
                chat_doc = self._update_dms_chat_document(chat_id, migration_details, user_id, schedule_name)

            if engine_type == "dlt":
                # TODO: figure out if we need dlt packages for DMS pipeline
                configurations = chat_doc.get("configurations", {})
                pipeline = chat_doc.get("history", [])
                dlt_packages_comma = self._dlt_packages(configurations, pipeline, user_id)
                dlt_packages_space = self._convert_packages_format(dlt_packages_comma)
                dag_data['conf']["pip_packages"] = dlt_packages_space
                
                dlt_conf = configurations.get("--conf", None) # TODO: Confirm if this conf gets stored in chat document or schedule document
                dag_data['conf']["dlt_conf"] = dlt_conf
            else:
                raise NotImplementedError(f"Engine type {engine_type} is not supported for DMS pipeline")
            
            data = ExportPipeline().prepare_schedule_data(
                job_id=str(chat_doc.get("_id", "")),
                user_id=user_id,
                schedule_interval=schedule_interval,
                advanced_scheduling=advanced_scheduling,
                pipeline=chat_doc.get("history", []),
                config=configurations,
                schedule_name=schedule_name,
                code=chat_doc.get("code", ""),
                engine_type=engine_type,
                generated_cron_expression=generated_cron_expression,
                replace_connections=None,
                notification=notification,
                export_files_list=[],
                type=chat_doc.get("type", "localstorage"),
                execution_type=execution_type,
                job_details=chat_doc.get("job_details", {}),
                export_format=None
            )
            
            data["meta_schedule_version"] = 2
            data["service_mode"] = "DMS"
            _, schedule_id = self.schedule_collection.insert_document(data)
            
            dag_data["conf"].update(
                {
                    "job_id": str(chat_doc.get("_id", "")),
                    "schedule_id": str(schedule_id),
                    "schedule_name": schedule_name,
                    "notification": notification
                }
            )
            if generated_cron_expression:
                dag_data["conf"]["generated_cron_expression"] = generated_cron_expression
                
            # TODO: check if need to support run now mode for DMS
            # create the dag
            if schedule_interval == "once" or schedule_interval is None:
                # This condition satisfies when create_dms_dag is called from "Run Now" button
                logger.info(f"Triggering run now dms for jobid - {chat_doc.get('_id', '')}, userid - {user_id}")
                run_now_data = {
                    "conf": {
                        "job_id": str(chat_doc.get("_id", "")),
                        "user_id": user_id,
                        "spark_path": "",
                        "spark_packages": "",
                        "execution_type": execution_type,
                        "helper_module": dag_data["conf"]["helper_module"],
                        "schedule_id": dag_data["conf"]["schedule_id"],
                        "engine_type": engine_type,
                        "pip_packages": dag_data["conf"].get("pip_packages", "")
                    }
                }
                response = self.call_api(RequestType.POST, "/api/v1/dags/run_now_dag/dagRuns", run_now_data)
            else:
                response = self.call_api(RequestType.POST, "/api/v1/dags/rest-trigger/dagRuns", dag_data)
            
            if 'error' in response:
                logger.debug("error in response")
                return response, 500
            
            logger.info(f"Successfully created DMS pipeline: {schedule_id} using schedule_id: {schedule_id}")
            return {
                "message": f"DMS pipeline {schedule_name} created successfully",
                "job_id": str(chat_doc.get("_id", "")),
                "run_id": str(response["dag_run_id"]),
                "engine_type": engine_type,
                "schedule_id": str(schedule_id),
                "cron_expression": generated_cron_expression
            }, 200
        except Exception as e:
            raise Exception(e) from e
        
    def delete_dms_dag(
        self, user_id: str, schedule_id: str
    ):
        try:
            response = self.call_api(RequestType.DELETE, f"/api/v1/dags/{schedule_id}")
            if 'error' not in response:
                logger.info(f"DAG {schedule_id} deleted from Airflow")
            else:
                raise RuntimeError("Unable to delete schedule in Airflow")
            
            success, schedule = self.schedule_collection.get_by_id(schedule_id)
            
            # Delete schedule collection entry
            self.schedule_collection.delete_one(schedule["_id"])
            self.chats_collection.delete_one(schedule["chat_id"])
            
            return {
                "message": f"DMS scheduled with id {schedule_id} deleted"
            }
        except Exception as e:
            logger.error(f"Failed to delete the DMS job", exc_info=True)
            raise RuntimeError("Unable to delete the DMS job") from e


    @Logger.generate
    def get_dms_run_history_info(self, schedule_id: str, chat_id: str, include_history: bool = False, history_limit: int = 20):
        if not hasattr(self, 'dms_progress_collection'):
            self.dms_progress_collection = MongoFactory(self.client, "dms_schedule_progress", session=self.session)
            
        _, schedule_doc = self.schedule_collection.get_by_id(schedule_id)
        migration_details = schedule_doc.get("pipeline", []) if schedule_doc else []
        # _, chat_doc = self.chats_collection.get_by_id(chat_id)
        # migration_details = chat_doc.get("history", []) if chat_doc else []
        
        run_history = []
        last_run = None
        
        try:
            run_cursor = self.dms_progress_collection.collection.find(
                {"schedule_id": str(schedule_id)}
            ).sort("started_at", -1).limit(history_limit)
            
            for run_doc in run_cursor:
                # Remove MongoDB _id
                run_doc.pop("_id", None)

                # Filter row_counts to exclude _dlt_ tables
                row_counts = run_doc.get("row_counts", {})
                filtered_row_counts = {
                    table: count for table, count in row_counts.items()
                    if not table.startswith("_dlt_")
                }
                run_doc["row_counts"] = filtered_row_counts
                
                run_history.append(run_doc)

            # Set last_run as the most recent run
            if run_history:
                last = run_history[0]
                last_run = {
                    "run_id": last.get("run_id"),
                    "status": last.get("status"),
                    "started_at": last.get("started_at"),
                    "completed_at": last.get("completed_at"),
                    "total_rows_transferred": last.get("total_rows_transferred", 0),
                    "duration_seconds": last.get("duration_seconds"),
                    "failed_step": last.get("failed_step"),
                    "error_message": last.get("error_message")
                }
        except Exception as e:
            logger.warning(f"Could not fetch run history for schedule {schedule_id}: {e}")

        response = {
            "migration_details": migration_details,
            "last_run": last_run
        }
        if include_history:
            response["run_history"] = run_history
            
        return response

    @Logger.generate
    def get_dms_schedule_info(
        self, user_id, schedule_id=None, include_history=True, history_limit=20
    ):
        """
        Get DMS schedule info with run history.
        If schedule_id is None, return all DMS schedules for the user. 
        Otherwise return the requested schedule.
        Includes is_paused status from Airflow.
        """
        if schedule_id is not None:
            _, schedule_doc = self.schedule_collection.get_by_id(schedule_id)
            user_schedules = [schedule_doc] if schedule_doc else []
        else:
            _, user_schedules = self.schedule_collection.get_all_by_user_id(user_id)
            
        schedules = []
        for schedule in user_schedules:
            # Filter only DMS schedules
            if schedule.get("service_mode", None) != "DMS":
                continue
            
            run_history_info = self.get_dms_run_history_info(
                schedule_id=str(schedule["_id"]),
                chat_id=schedule["chat_id"],
                include_history=include_history,
                history_limit=history_limit
            )
            
            schedule_details = {
                "_id": str(schedule["_id"]),
                "schedule_name": schedule.get("schedule_name", "NA"),
                "service_type": "dms",
                "migration_details": run_history_info["migration_details"],
                "last_run": run_history_info["last_run"]
            }
            
            if include_history:
                schedule_details["run_history"] = run_history_info.get("run_history", [])
            
            # Fetch status from Airflow
            try:
                dag_id = str(schedule["_id"])
                dag_info = self.call_api(RequestType.GET, f"/api/v1/dags/{dag_id}")
                
                if 'error' not in dag_info:
                    is_paused = dag_info.get("is_paused", False)
                    schedule_details["status"] = "paused" if is_paused else "active"
                else:
                    schedule_details["status"] = "active"
                    
            except Exception as e:
                logger.warning(f"Could not fetch DAG status from Airflow for {schedule['_id']}: {e}")
                schedule_details["status"] = "unknown"
                
            schedules.append(schedule_details)
            
        return {
            "success": True,
            "schedules": schedules
        }
            
    @Logger.generate
    def delete_dag(self, job_id):
        """
        Delete a DAG (Directed Acyclic Graph) with the provided job_id.

        :param job_id: The unique identifier for the DAG to be deleted.
        :type job_id: str
        :return: A response indicating the success or failure of DAG deletion.
                - If the DAG doesn't exist, it returns a 404 error message.
                - If the deletion is successful, it returns a success message.
                - If there's an error during deletion, it returns the error response.
        :rtype: dict
        """
        if not self.dag_exists(job_id):
            logger.info("DAG does not exist")
            return {"message": "DAG does not exist"}, 404

        response = self.call_api(RequestType.DELETE, f"/api/v1/dags/{job_id}")
        if 'error' not in response:
            logger.info(f"DAG {job_id} deleted successfully")
            return {"message": f"DAG {job_id} deleted successfully"}, 200
        else:
            logger.debug(response)
            return response
        
    def _parse_schedule_start_date_time_to_str(self, advanced_scheduling) -> Optional[str]:
        start_date = advanced_scheduling.get('StartDate', None)
        start_time = advanced_scheduling.get('StartTime', None)
        time_zone = advanced_scheduling.get('timeZone', None)

        if start_date is None or start_time is None or time_zone is None:
            return None
        
        # Combine date and time strings
        datetime_str = f"{start_date} {start_time}"

        # Create naive datetime object
        naive_dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

        # Attach timezone
        tz = pytz.timezone(time_zone)
        localized_dt = tz.localize(naive_dt)

        return localized_dt.isoformat()
    
    def _get_start_date_time_for_dag(self, dag_id: str) -> Optional[str]:
        try:
            success, schedule = self.schedule_collection.get_by_id(dag_id)
        except Exception as e:
            logger.error(str(e))
            return None
        
        if success:
            return self._parse_schedule_start_date_time_to_str(schedule['advanced_scheduling'])
        else:
            return None

    @Logger.generate   
    def _get_details_for_db_connection(self, connection_id: str, table_name: str) -> tuple:
        """
        Get connection details for database connection.
        
        :param connection_id: The connection ID
        :return: Tuple of (connection_alias, connection_type)
        """
        try:
            status, connection = self.connections_collection.get_by_id(connection_id)
            if status and connection:
                connection_alias = connection.get('connection_alias', table_name)
                connection_type = connection.get('type', 'table')
            else:
                connection_alias = table_name
                connection_type = 'table'
        except Exception as e:
            logger.warning(f"Could not fetch connection details for {connection_id}: {str(e)}")
            connection_alias = table_name
            connection_type = 'table'
        
        return connection_alias, connection_type

    @Logger.generate
    def _get_details_for_file_connection(self, file_id: str, file_name: str) -> str:
        """
        Get file type details for file connection.
        
        :param file_id: The file ID
        :param file_name: The file name
        :return: File type string
        """
        file_type = 'n/a'  # Default file type for cases where file might be deleted 
        try:
            file_success, file_data = self.files_collection.get_by_file_id_and_file_name(file_id, file_name)
            if file_success and file_data:
                files_array = file_data.get('files', [])
                for file_obj in files_array:
                    if file_obj.get('file_id') == file_id and file_obj.get('file_name') == file_name:
                        raw_file_type = file_obj.get('file_type', '.n/a')
                        file_type = raw_file_type.lstrip('.')
                        break
        except Exception as e:
            logger.warning(f"Could not fetch file details for {file_id}: {str(e)}")
        return file_type
    
    @Logger.generate
    def _format_configuration(self, schedule):
        """
        Format configuration dictionary into a list of dictionaries with configKey and configValue.
        
        :param schedule: Schedule document
        :type schedule: dict
        :return: List of dictionaries with configKey and configValue
        :rtype: list
        """
        try:
            formatted_config = []
            configuration = schedule.get("configurations", {})
            
            for key, value in configuration.items():
                if isinstance(value, (dict, list)):
                    # Convert dict to JSON string with double quotes
                    config_value = json.dumps(value, separators=(',', ':'))
                elif isinstance(value, str):
                    # Keep string values as-is
                    config_value = value
                else:
                    # Convert other types (int, float, bool, None) to JSON string
                    config_value = json.dumps(value, separators=(',', ':'))
                
                formatted_config.append({
                    'configKey': key,
                    'configValue': config_value
                })
                
        except Exception as e:
            logger.warning(f"Error formatting configuration: {str(e)}")
            return []
            
        return formatted_config
    
    @Logger.generate
    def _reverse_format_configuration(self, formatted_config):
        """
        Reverse format configuration from a list of dictionaries with configKey and configValue
        back to the original configuration dictionary format.
        
        :param formatted_config: List of dictionaries with configKey and configValue
        :type formatted_config: list
        :return: Original configuration dictionary
        :rtype: dict
        """
        try:
            configuration = {}
            
            for config_item in formatted_config:
                key = config_item.get('configKey')
                value = config_item.get('configValue')
                
                if key is None or value is None:
                    continue
                    
                try:
                    # Try to parse as JSON first (for dict, list, int, float, bool, None)
                    parsed_value = json.loads(value)
                    configuration[key] = parsed_value
                except (json.JSONDecodeError, TypeError):
                    # If JSON parsing fails, treat as string
                    configuration[key] = value
                    
        except Exception as e:
            logger.warning(f"Error reversing configuration format: {str(e)}")
            return {}
            
        return configuration

    def _get_read_tables_details(self, parameters: dict, output: dict) -> dict:
        """
        Handle read_tables pipeline step and return file details.
        
        :param parameters: Step parameters
        :param output: Step output
        :return: File details dictionary or None if invalid
        """
        connection_id = parameters.get('connection_id')
        if not connection_id:
            return None
            
        table_name = parameters.get('table_name', '')
        dataframe_alias = output.get('dataframe_alias', '')
        source_id = output.get('source_id', '')
        
        connection_alias, connection_type = self._get_details_for_db_connection(connection_id, table_name)
        
        return {
            'alias': dataframe_alias,
            'type': 'table',
            'source_id': source_id,
            '_id': connection_id,
            'connection_type': connection_type,
            'connection_alias': connection_alias
        }

    def _get_read_files_details(self, parameters: dict, output: dict) -> dict:
        """
        Handle read_files pipeline step and return file details.
        
        :param parameters: Step parameters
        :param output: Step output
        :return: File details dictionary or None if invalid
        """
        file_id = parameters.get('file_id')
        file_name = parameters.get('file_name', '')
        if not file_id or not file_name:
            return None
            
        dataframe_alias = output.get('dataframe_alias', '')
        source_id = output.get('source_id', '')
        
        file_type = self._get_details_for_file_connection(file_id, file_name)
        
        return {
            'alias': dataframe_alias,
            'type': file_type,
            'source_id': source_id,
            '_id': file_id,
            'connection_type': 'file',
            'connection_alias': file_name
        }


    @Logger.generate
    def _get_dag_files_and_destination_list_from_pipeline(self, pipeline) -> tuple[list, list]:
        """
        Get files_list that are exported ,advanced_scheduling and destination details for a specific DAG.
        For export operations, only return files that are actually being exported.
        
        :param schedule: Schedule document from db
        :type schedule: dict
        :return: Tuple containing (filtered_files_list, advanced_scheduling, destination_list)
        :rtype: tuple[list, dict, list]
        """
        try:
            all_files_list = []
            destination_list = []
            export_source_ids = set()  # Track source_ids that are being exported
            
            # First pass: Collect all files and identify export source_ids
            for step in pipeline:
                function = step.get('function', '')
                parameters = step.get('parameters', {})
                output = step.get('output', {})

                # Handle source files/tables (read operations)
                if function == 'read_tables':
                    file_details = self._get_read_tables_details(parameters, output)
                    if file_details:
                        all_files_list.append(file_details)
                        
                elif function == 'read_files':
                    file_details = self._get_read_files_details(parameters, output)
                    if file_details:
                        all_files_list.append(file_details)

                # Handle destination (export operations) and collect export source_ids
                elif function in ['export', 'export_table']:
                    source_id = parameters.get('source_id', '')
                    
                    if source_id:
                        export_source_ids.add(source_id)  # Track this source_id for filtering
                    
                    if function == 'export':
                        # Destination is local storage.
                        destination_list.append({
                            'destination': 'localstorage',
                            'source_id': source_id
                        })
                    
                    elif function == 'export_table':
                        # Destination is database for export_table function
                        connection_id = parameters.get('connection_id', '')
                        table_name = parameters.get('table_name', '')
                        
                        if connection_id and table_name:
                            connection_alias, connection_type = self._get_details_for_db_connection(connection_id, table_name)
                            
                            destination_list.append({
                                'destination': 'database',
                                'connection_id': connection_id,
                                'catalog': table_name,
                                'database': connection_id,  
                                'source_id': source_id,
                                'connection_name': connection_alias
                            })
            
            # Filter files_list to only include files that are being exported
            if export_source_ids:
                filtered_files_list = [
                    file_item for file_item in all_files_list
                    if file_item.get('source_id') in export_source_ids
                ]
            else:
                # If no exports found, return all files (fallback behavior)
                filtered_files_list = all_files_list
            
            return filtered_files_list, destination_list
        except Exception as e:
            logger.error(f"Error extracting files list, advanced scheduling, and destinations for pipeline: {str(e)}")
            return [], []
        
    @staticmethod
    def _get_details_from_tags(dag: Mapping, chat_name):
        data = {}
        tags = dag.get('tags', [])
        
        for tag1 in tags:
            if tag1.get('name', '').startswith("job_name"):
                data["job_name"] = chat_name
                prefix, _ = tag1['name'].split(":", 1)
                tag1['name'] = f"{prefix}:{chat_name}"
            elif tag1.get('name', '').startswith("local"):
                try:
                    data["local"]=ast.literal_eval(tag1.get('name', '').split(":")[1])
                except:
                    data["local"]="na"
            elif tag1.get('name', '').startswith("schedule_name"):
                data["schedule_name"]=tag1.get('name', '').split(":")[1]
            elif tag1.get("name", "").startswith("service_type"):
                data["service_type"]=tag1.get('name', '').split(":")[1]
                
        # Set default service_type as dts (data tranformation service) for older dags
        if "service_type" not in data:
            data["service_type"] = "dts"
        
        return data

    def _extract_chat_name(self, dag):
        _, schedule = self.schedule_collection.get_by_id(dag['dag_id'])
        if schedule is None:
            return None, None, None
        _, chat = self.chats_collection.get_by_id(schedule.get("chat_id"))
        if chat is None:
            return None, None, None
        chat_name = chat.get("chat_name", "NA")
        return chat_name, chat, schedule

    def _prepare_dag_runs(self, dags, user_id, ignore_fields: dict = None):
        user_dags = {"dags": []}
        for dag in dags:
            chat_name, chat, schedule = self._extract_chat_name(dag)
            if schedule is None or chat is None:
                logger.error(f"Requested data with schedule_id {dag['dag_id']} not found")
                continue
            dag.update(AirflowAPI._get_details_from_tags(dag, chat_name))

            if (start_date_time := self._get_start_date_time_for_dag(dag['dag_id'])) is not None:
                dag["starts_on"] = start_date_time

            if ignore_fields and all(schedule.get(key) == value for key, value in ignore_fields.items()):
                continue
            configuration = self._format_configuration(schedule)
            files_list = schedule.get("export_files_list", None)
            advanced_scheduling = schedule.get("advanced_scheduling", None)
            destination = None
            
            dag["schedule_id"] = str(schedule.get("_id"))
            dag["schedule_name"] = schedule.get("schedule_name", "-")
            
            #  Show the pre-generated cron expression
            if schedule.get("generated_cron_expression"):
                dag["cron_expression"] = schedule.get("generated_cron_expression")
                logger.info(f"Using pre-generated cron expression: {schedule.get('generated_cron_expression')}")
            
            dag["meta_schedule_version"] = schedule.get("meta_schedule_version", 1)
            if "export_files_list" in schedule:
                dag["meta_schedule_version"] = 2
            
            # Handle old schedule format
            if dag["meta_schedule_version"] == 1:
                files_list, destination = self._get_dag_files_and_destination_list_from_pipeline(schedule.get("pipeline", []))
            
                # Create job_details object containing all the job-related information
                dag["job_details"] = {
                    "configuration": configuration,
                    "files_list": files_list,
                    "destination": destination,
                    "advanced_scheduling": advanced_scheduling
                }
            else:
                history = ExportPipeline().export_pipeline(
                    schedule.get("chat_id"), user_id,
                    schedule.get("job_details", {}),
                    chat, schedule.get("execution_type", "pipeline")
                )
                files_list, destination = self._get_dag_files_and_destination_list_from_pipeline(history)
                dag["job_details"] = {
                    "configuration": configuration,
                    "files_list": files_list,
                    "export_files_list": schedule.get("export_files_list", []),
                    "destination": destination,
                    "advanced_scheduling": advanced_scheduling,
                    "schedule_interval": schedule.get("generated_cron_expression") if schedule.get("generated_cron_expression") else schedule.get("schedule_interval", "once"),
                    "engine_type": schedule.get("engine_type", "spark"),
                    "notification": schedule.get("notification", {}),
                    "replace_connections": schedule.get("replace_connections", {})
                }
                
            if dag.get("service_type") == "dms":
                dms_run_history_info = self.get_dms_run_history_info(
                    schedule_id=str(schedule.get("_id")),
                    chat_id=schedule.get("chat_id"),
                    include_history=False,
                    history_limit=20
                )
                if dms_run_history_info is None:
                    dag["migration_details"] = []

                dag["migration_details"] = dms_run_history_info.get("migration_details", "last_run")
                if "last_run" in dms_run_history_info and dms_run_history_info["last_run"] is not None:
                    dag["last_run"] = {
                        "status": dms_run_history_info["last_run"].get("status", "FAILED"),
                        "total_rows_transferred": dms_run_history_info["last_run"].get("total_rows_transferred", 0),
                        "failed_step": dms_run_history_info["last_run"].get("failed_step", "")
                    }
                
            user_dags["dags"].append(dag)
        return user_dags
    
    def _clean_dags(self, dags_list):
        keys_to_keep = ["cron_expression", "dag_display_name", "dag_id", "is_active", "is_paused", "job_details", "job_name", "local", "meta_schedule_version", "next_dagrun", "next_dagrun_create_after", "next_dagrun_data_interval_end", "next_dagrun_data_interval_start", "owners", "schedule_id", "schedule_interval", "schedule_name", "starts_on", "tags", "timetable_description"]
        cleaned_dags_list = [
            {key: dag[key] for key in keys_to_keep if key in dag}
            for dag in dags_list
        ]
        return cleaned_dags_list
    
    @Logger.generate
    def get_dag_search_filters(self, user_id, ignore_fields: dict = None):
        try:
            # TODO: Instead of hardcoding service_types, we can extract them from schedules
            service_types = ["dts", "dms"]
            _, schedule = self.schedule_collection.get_all_by_user_id(user_id)
            schedule = list(schedule) if schedule else []
            if not schedule:
                return {"success": True, "dag_search_filters": {"schedule_names": [], "job_names": [], "service_types": service_types}, "msg": "Dag search filters retrieved successfully."}, 200
            if ignore_fields:
                data = list([sch for sch in schedule if not all(sch.get(key) == value for key, value in ignore_fields.items())])
            else:
                data = schedule
            # For run now schedules, we will have generated_cron_expression as None, so filtering out those records. Old schedules have schedule interval as once.
            schedules = [record for record in data if 'generated_cron_expression' not in record or record.get('generated_cron_expression') is not None]
            schedule_names = list(set([record.get('schedule_name') for record in schedules]))
            chat_ids = list(set([record.get('chat_id') for record in schedules]))
            job_names = []
            for chat_id in chat_ids:
                if chat_id is None:
                    logger.warning("Chat ID is None for schedule")
                    continue
                _, chats = self.chats_collection.get_by_id(chat_id)
                if not chats:
                    logger.warning(f"Chat not found for chat_id: {chat_id}")
                    continue
                job_names.append(chats.get("chat_name"))
            
            return {"success": True, "dag_search_filters": {"schedule_names": schedule_names, "job_names": job_names, "service_types": service_types}, "msg": "Dag search filters retrieved successfully."}, 200
        except Exception as e:
            logger.error(str(e), exc_info=True)
            return  {"success": False, "msg": f"{e}"}, 500

    @Logger.generate
    def get_dag_runs(self, req_data, ignore_fields: dict = None):
        """
        Get a list of DAG (Directed Acyclic Graph) runs.

        :param user_id: The ID of the user to filter DAGs.
        :type user_id: str
        :return: A response containing the list of DAG runs.
        :rtype: dict
        """
        filter_applied = False
        user_id = req_data["user_id"]
        page = int(req_data.get('page')) if req_data.get('page') and int(req_data.get('page')) > 0 else 1
        if req_data.get('per_page') is None or int(req_data.get('per_page')) <= 0:
            per_page = int(self.config["api"]["preview_default_per_page"])
        else:
            per_page = min(int(req_data.get('per_page')), int(self.config["api"]["preview_max_per_page_limit"]))
        offset = (page - 1) * per_page

        prefix = "user_id:"
        final_tags = [f"{prefix}{user_id.strip()}"]
        for key in ["schedule_name", "job_name"]:
            value = req_data.get(key)
            if value:
                filter_applied = True
                for val in value:
                    final_tags.append(f"{key}:{val}")
        tags_param = [("tags", tag) for tag in final_tags]
        tags_param = urlencode(tags_param)

        if filter_applied:
            # TODO: Directly filter the dags from mongo based on schedule_name and job_name
            response = self.call_api(RequestType.GET, f"/api/v1/dags?{tags_param}&order_by=-dag_id")
            matching_dags = []
            tag_groups = defaultdict(set)
            for tag in final_tags:
                prefix = tag.split(":", 1)[0]
                tag_groups[prefix].add(tag)
            for dag in response.get("dags", []):
                chat_name, _, _ = self._extract_chat_name(dag)
                dag.update(AirflowAPI._get_details_from_tags(dag, chat_name))
                dag_tags = {t["name"] for t in dag.get("tags", [])}
                
                # Set default service_type as aod for older dags
                if "service_type:dts" not in dag_tags and "service_type:dms" not in dag_tags:
                    dag_tags.add("service_type:dts")
                
                # Skip if required user_id is not present
                user_tag = next((t for t in final_tags if t.startswith("user_id:")), None)
                if user_tag and user_tag not in dag_tags:
                    continue
                # Check that each other tag group (except user_id) has at least one match
                tag_group_match = True
                for prefix, tags in tag_groups.items():
                    if prefix == "user_id":
                        continue  # already checked
                    if not any(tag in dag_tags for tag in tags):
                        tag_group_match = False
                        break
                if tag_group_match:
                    matching_dags.append(dag)
            total_dags = len(matching_dags)
            paginated_dags = matching_dags[offset:offset + per_page]
            response = {"dags": paginated_dags, "total_entries": total_dags}
        else:
            response = self.call_api(RequestType.GET, f"/api/v1/dags?limit={per_page}&offset={offset}&{tags_param}&order_by=-dag_id")
        
        dags = response.get('dags', [])
        dags = self._clean_dags(dags)
        total_entries = response.get('total_entries', 0)
        user_dags = self._prepare_dag_runs(dags, user_id, ignore_fields)
        if user_dags is not None:
            logger.info("Successfully fetched the schedules")
            return {"dags":user_dags["dags"], "page": page, "per_page": per_page, "total_records": total_entries}
        else:# pragma: no cover
            logger.error("Failed to fetch the schedules", exc_info=True)
            raise Exception(f"Failed to fetch the schedules with req_data: {req_data}")

    def _parse_query_params(self, query_params):
        return {
            "page": int(query_params.get("page", 1)),
            "per_page": int(query_params.get("per_page", 10)),
            "sort_field": query_params.get("sort_field", "execution_date"),
            "sort_order": query_params.get("sort_order", "desc"),
            "start_date": query_params.get("start_date"),
            "end_date": query_params.get("end_date"),
            "state": query_params.get("state")
        }

    @Logger.generate
    def get_dag_info(self, job_id, query_params={}):
        """
        Get information about a specific DAG (Directed Acyclic Graph).

        :param job_id: The unique identifier for the DAG.
        :type job_id: str
        :return: A response containing the information about the DAG.
        :rtype: dict
        """
        params = self._parse_query_params(query_params)
        response_data = {}
        final_tags = defaultdict(list)
        if params.get("start_date") and params.get("end_date"):
            final_tags["execution_date_gte"] = params["start_date"]
            final_tags["execution_date_lte"] = params["end_date"]
        if params.get("state"):
            state_values = [s.strip() for s in params["state"].split(",") if s.strip()]
            if state_values:
                final_tags["state"] = state_values
        # Retrieve basic info about the DAG
        dag_info = self.call_api(RequestType.GET, f"/api/v1/dags/{job_id}")
        response_data['basic_info'] = dag_info
        tags = dag_info.get('tags', [])
        for tag in tags:
                if tag.get('name', '').startswith("job_name"):
                    response_data['basic_info']["job_name"]=tag.get('name', '').split(":")[1]
                elif tag.get('name', '').startswith("local"):
                    response_data['basic_info']["local"]=ast.literal_eval(tag.get('name', '').split(":")[1])
                else:
                   pass

        page = int(params["page"]) if params.get("page") and int(params["page"]) > 0 else 1
        if params.get("per_page") is None or int(params["per_page"]) <= 0:
            per_page = int(self.config["api"]["preview_default_per_page"])
        else:
            per_page = min(int(params["per_page"]), int(self.config["api"]["preview_max_per_page_limit"]))
        offset = (page - 1) * per_page
        order_prefix = "-" if params["sort_order"].lower() == "desc" else ""
        order_by_param = f"&order_by={order_prefix}{params['sort_field']}" if params["sort_field"] else ""
        tags_param = "&" + urlencode(final_tags, doseq=True) if final_tags else ""
        dag_runs_resp = self.call_api(
            RequestType.GET,
            f"/api/v1/dags/{job_id}/dagRuns?limit={per_page}&offset={offset}{order_by_param}{tags_param}"
        )
        dag_runs = dag_runs_resp.get('dag_runs', [])
        total_entries = dag_runs_resp.get("total_entries", 0)
        response_data['dag_runs'] = {
            "dag_runs": dag_runs,
            "page": page,
            "per_page": per_page,
            "total_entries": total_entries
        }

        # Retrieve tasks associated with the DAG
        tasks = self.call_api(RequestType.GET, f"/api/v1/dags/{job_id}/tasks")
        response_data['tasks'] = tasks

        # logger.info(response_data)
        return response_data

    @Logger.generate
    def pause_dag(self, job_id, req_data):
        """
        Pause the dag based on the given id
        :param job_id: The unique identifier for the DAG.
        :return: 
        """
        try:
            is_paused = req_data.get("is_paused")
            pause_response = self.call_api(RequestType.PATCH, f"/api/v1/dags/{job_id}", payload={"is_paused": is_paused})
            if 'error' in pause_response:
                logger.debug(pause_response)
                return {"success": False, "message":f"Failed to pause DAG {job_id}"}, 404
            else:
                if is_paused== True:
                    message=f"Paused DAG successfully."
                else:
                    message=f"Unpaused DAG successfully."
                response = {"success": True,
                            "message":message}
                return response, 200
        except Exception as e: # pragma: no cover
            response = {"success": False,
                        "message": f"Failed to pause DAG {job_id}: {str(e)}"}
            return response, 404

    @Logger.generate
    def get_user_dags(self, user_id):
        """
        Get a list of DAGs (Directed Acyclic Graphs) associated with a specific user.

        :param user_id: The ID of the user to filter DAGs.
        :return: A dictionary containing the following information:
                - 'user_id': The ID of the user.
                - 'user_dags': List of DAGs associated with the user, including their 'dag_id' and 'schedule_interval'.
        """
        dags = self.get_dag_runs(user_id)
        user_dags = []

        for dag in dags.get('dags', []):
            tags = dag.get('tags', [])
            for tag in tags:
                if tag.get('name', '').endswith(user_id):
                    user_dags.append({
                        "dag_id": dag['dag_id'],
                        "schedule_interval": dag.get('schedule_interval', {}).get('value', ''),
                    })

        return {
            "user_id": user_id,
            "user_dags": user_dags
        }

    @Logger.generate 
    def stream_dag_log(self, job_id, dag_run_id, engine_type):
        """
        Stream logs for the given dag run based on engine type
        """
        if "manual" in dag_run_id:
            logger.info(f"dag run id found as run now for engine_type: {engine_type}")
            
            # Determine task instance based on engine type
            if engine_type and engine_type.lower() == "dlt":
                task_instance = "run_now_dlt_task"
                logger.info("Using DLT task instance for log streaming")
            else:
                task_instance = "run_now_job_task"  # Default to Spark
                logger.info("Using Spark task instance for log streaming (default)")
                
            logs_url = f"/api/v1/dags/run_now_dag/dagRuns/{dag_run_id}/taskInstances/{task_instance}/logs/1"
            logger.info(f"Logs URL: {logs_url}")
            
        else:
            # Note: streaming is only enabled for run_now jobs
            logger.error("Tried streaming for scheduled job. Streaming logs is only supported for 'run_now' jobs")
            return Response("Streaming not supported for scheduled jobs", status=400, mimetype="text/plain")

        def stream():
            try:
                yield "data: ----Streaming logs for the run----\n\n"
                continuation_token = None
                is_log_complete = False # We consider logs to be complete once there is status of the task marked in logs
                
                while True:
                    time.sleep(1)
                    sys.stdout.flush()
                    
                    if continuation_token is not None:
                        new_logs_url = logs_url + f"?token={continuation_token}"
                    else:
                        new_logs_url = logs_url

                    logs_response = self.call_api(RequestType.GET, new_logs_url, expect_json=True)
                    content, continuation_token = logs_response['content'], logs_response['continuation_token']

                    try:
                        decoded = ast.literal_eval(content)[0][1]
                    except Exception as e:
                        logger.info(f"Unable to extract only chunk data - {e}")
                        decoded = content

                    # Check for completion markers 
                    if "Marking task as FAILED" in decoded or "Marking task as SUCCESS" in decoded:
                        is_log_complete = True

                    processed_log = decoded.replace(". ", ".\n")

                    yield "data: " + processed_log + "\n\n"

                    if is_log_complete:
                        yield "event: finished\n"
                        yield "data: -----End of log streaming----\n\n"
                        break
                        
            except Exception as e:
                logger.error(f"Error while streaming logs for engine_type {engine_type} - {e}")
                return Response(f"Error while streaming logs: {str(e)}", status=500, content_type="text/plain")

        return Response(stream(), content_type="text/event-stream")


    @Logger.generate
    def get_dag_log(self, job_id,dag_run_id,engine_type):
        """
        Get the logs for the latest DAG run associated with a job_id.

        :param job_id: The unique identifier for the DAG.
        :return: A response containing the logs for the latest DAG run, or appropriate error messages.
        """

        if "manual" in dag_run_id:
            # Note: If dag was triggered with "RUN NOW" the dag_run_id has "manual" in its string
            logs_url = f"/api/v1/dags/run_now_dag/dagRuns/{dag_run_id}/taskInstances/run_now_job_task/logs/1"

        else:
            # Fetch Tasks
            tasks_url = f"/api/v1/dags/{job_id}/dagRuns/{dag_run_id}/taskInstances"
            tasks_response = self.call_api(RequestType.GET, tasks_url)
            
            if 'error' in tasks_response or not tasks_response.get('task_instances'):
                logger.error(f'No tasks found for DAG run_id: {dag_run_id}', exc_info=True)
                return "No tasks found for DAG run_id: {}".format(dag_run_id), 404

            # Get the task_id of the first task in the DAG run
            try:
                task_id = tasks_response['task_instances'][1]['task_id']
            except:
                task_id = tasks_response['task_instances'][0]['task_id']

            if engine_type == "dlt":
                logs_url = f"/api/v1/dags/{job_id}/dagRuns/{dag_run_id}/taskInstances/run_dlt_task/logs/1"
            else:
                logs_url = f"/api/v1/dags/{job_id}/dagRuns/{dag_run_id}/taskInstances/submit_spark_app/logs/1"

        logs_response = self.call_api(RequestType.GET, logs_url, expect_json=False)
        
        # Process and format the logs for readability
        processed_log = logs_response.replace(". ", ".\n")
        # logger.info(processed_log)
        return processed_log, 200

    def _verify_start_date_constraint_for_dag(self, dag_id):
        start_date_time_str = self._get_start_date_time_for_dag(dag_id)
        
        if start_date_time_str is None:
            return True
        
        start_dt = datetime.fromisoformat(start_date_time_str)

        # Step 2: Get the current time in the same timezone
        tz = pytz.timezone("Asia/Calcutta")
        now = datetime.now(tz)
        
        return now > start_dt

    @Logger.generate
    def trigger_dag(self, req_data):
        """
        Trigger a DAG (Directed Acyclic Graph) run.

        :param req_data: A dictionary containing the data required to trigger the DAG.
        :type req_data: dict
        :param req_data['dag_id']: The unique identifier for the DAG to be triggered.
        :type req_data['dag_id']: str
        :param req_data.get('execution_date'): The execution date for the DAG run, defaults to current date and time.
        :type req_data.get('execution_date'): datetime, optional
        :return: A response indicating the success or failure of DAG triggering.
        :rtype: dict
        :return: 
            - success (bool): Indicates whether the DAG was triggered successfully.
            - message (str): A message providing more information about the result of the DAG triggering.
        """
        dag_id = req_data.get('dag_id')
        
        if not dag_id:
            logger.error('dag_id is required', exc_info=True)
            return {"success": False, "text": "dag_id is required"}, 400

        if not self._verify_start_date_constraint_for_dag(dag_id):
            return {"success": False, "message": "manual trigger is not allowed before dag start time"}, 400
        
        try:
            # Call Airflow API to check DAG run information
            uniq_id = str(uuid.uuid4())
            response = self.call_api(RequestType.POST, f"/api/v1/dags/{dag_id}/dagRuns", payload={"dag_run_id":uniq_id})
            if 'error' not in response:
                # logger.info(f"API response: {response}")
                logger.info("DAG triggered successfully")
                return {"success": True, "message": "DAG triggered successfully"}, 200
            else:
                raise Exception("failed to execute dag")
        except Exception as e:
            logger.error(str(e), exc_info=True)
            return {"success": False, "message": str(e)}, 500

    @Logger.generate
    def get_dag_run_status(self, req_data):
        """
        Get the DAG run status (state) for a specific dag_run_id of a dag_id.

        :param req_data: Dict containing 'dag_run_id' and optional 'dag_id'
        :return: Dict with success flag and state information
        """
        dag_run_id = req_data.get('dag_run_id')
        dag_id = req_data.get('dag_id') or 'run_now_dag'

        if not dag_run_id:
            logger.error('dag_run_id is required', exc_info=True)
            return {"success": False, "msg": "dag_run_id is required"}, 400

        try:
            # Fetch specific DAG run details
            resp = self.call_api(RequestType.GET, f"/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}")

            if 'error' in resp:
                return {"success": False, "msg": resp.get('error', 'Failed to fetch dag runs')}, resp.get('status_code', 500)

            state = resp.get('state')
            return {"success": True, "dag_id": dag_id, "dag_run_id": dag_run_id, "state": state}, 200
        except Exception as e:
            logger.error(str(e), exc_info=True)
            return {"success": False, "msg": str(e)}, 500

    @Logger.generate
    def schedule_exists(self, schedule_id):
        """
        Function to check if a Schedule exists.

        :param schedule_id: The ID of the schedule to check.
        :return: True if the schedule exists, False otherwise.
        """
        response = self.call_api(RequestType.GET, f"/api/v1/dags/{schedule_id}")
        return 'error' not in response

    @Logger.generate
    def delete_schedule(self, payload):
        """
        Delete a schedule for a given job and schedule ID.

        :param schedule_id: The unique identifier for the schedule to be deleted.
        :type schedule_id: str
        :param job_id: The unique identifier for the job associated with the schedule.
        :type job_id: str
        :return: A response indicating the success or failure of schedule deletion.
                - If the schedule doesn't exist, it returns a 404 error message.
                - If the deletion is successful, it returns a success message.
                - If there's an error during deletion, it returns the error response.
        :rtype: dict
        """
        response_err = []
        response_succ = []
        schedule_ids = payload.get("schedule_ids", [])
        for schedule_id in schedule_ids:
            if not self.schedule_exists(schedule_id): # pragma: no cover
                logger.info("Schedule does not exist")
                response_err.append(f"Schedule with {schedule_id} does not exist")
                continue
            
            # Step 1: Pause the DAG
            pause_response = self.call_api(RequestType.PATCH, f"/api/v1/dags/{schedule_id}", payload={"is_paused": True})
            if 'error' in pause_response:
                logger.debug(pause_response)
                response_err.append(f"Failed to pause DAG {schedule_id}")
                continue

            # Step 2: Delete the DAG .py file from the dags folder
            # Do this before removing from Airflow DB and MongoDB so that if the
            # file removal fails we haven't already lost the schedule record.
            dag_file_path = os.path.join(self.dag_path, "dags", f"{schedule_id}.py")
            if os.path.exists(dag_file_path):
                try:
                    os.remove(dag_file_path)
                    logger.info(f"DAG file {dag_file_path} deleted successfully")
                except OSError as e:
                    logger.error(f"Failed to delete DAG file {dag_file_path}: {e}")
                    response_err.append(f"Failed to delete DAG file for {schedule_id}: {e}")
                    continue
            else:
                logger.warning(f"DAG file {dag_file_path} does not exist, proceeding with DB cleanup anyway")

            # Step 3: Delete the DAG from Airflow's metadata database
            response = self.call_api(RequestType.DELETE, f"/api/v1/dags/{schedule_id}")
            if 'error' in response: # pragma: no cover
                logger.debug(response)
                response_err.append(f"Failed to delete DAG {schedule_id} from Airflow")
                continue

            # Step 4: Delete the schedule document from MongoDB (last, after all other steps succeed)
            self.schedule_collection.delete_one(schedule_id)
            logger.info(f"Schedule {schedule_id} deleted successfully")
            response_succ.append(schedule_id)

        response = {
            "success" : response_succ,
            "errors" : response_err
        }
        return response, 200

    @Logger.generate
    def edit_schedule(self, schedule_id, data, user_id):
        """
        Edit schedule with given schedule_id. Fields in "data" dictionary will be used to update
        fields in the schedule document
        """
        _, schedule = self.schedule_collection.get_by_id(str(schedule_id))
        
        if schedule is None:
            logger.error(f"No schedule found for schedule id {schedule_id}")
            return {
                "success": False,
                "msg": "No schedule found for given schedule id"
            }, 400
            
        _, chat = self.chats_collection.get_by_id(schedule.get("chat_id"))
        pipeline = None
        try:
            pipeline = ExportPipeline().export_pipeline(
                schedule.get("chat_id"),
                schedule.get("user_id"),
                schedule.get("job_details", {}),
                chat,
                schedule.get("execution_type", "pipeline")
            )
        except Exception as e:
            logger.warning(f"Could not reconstruct pipeline for packages: {e}")
        
        configurations=chat.get("configurations",{})
        
        if chat is None:
            logger.error(f"No chat found for schedule id {schedule_id}")
            return {
                "success": False,
                "msg": "No chat found related to given schedule id"
            }, 400
            
        replace_connections = data.get("replace_connections", {})
        packages = self._packages(configurations, pipeline, user_id, replace_connections)
        # parsing data
        if "job_details" in data:
            if "files_list" in data["job_details"]:
                data["export_files_list"] = data["job_details"]["files_list"]
            if "type" in data["job_details"]:
                data["type"] = data["job_details"]["type"]
                
            data.pop("job_details")
            
        if "executionType" in data:
            data["execution_type"] = data["executionType"]
            data.pop("executionType")
            
        if "upgrade_schedule_version" in data:
            if data["upgrade_schedule_version"] == 2:
                if "execution_type" not in data:
                    raise ValueError("Invalid request. `execution_type` is required to upgrade schedule version")
                # upgrade to version 2
                data["meta_schedule_version"] = 2
                data.pop("upgrade_schedule_version")
        
        updatable_fields = [
            "schedule_name", "schedule_interval", "advanced_scheduling", 
            "configurations", "replace_connections", "notification",
            "export_files_list", "type", "engine_type", "execution_type",
            "meta_schedule_version"
        ]

        if schedule["user_id"] != user_id:
            raise ValueError("Invalid request. User can only modify schedule created by them.")
        
        for field, _ in data.items():
            if field not in updatable_fields:
                raise ValueError(f"Invalid request. Field {field} is not updatable")
            
        if "execution_type" in data and not self.is_valid_execution_type(data["execution_type"]):
            raise ValueError(f"Invalid execution_type {data['execution_type']}, valid values are `pipeline` or `code`")
        if "engine_type" in data and not self.is_valid_engine_type(data["engine_type"]):
            raise ValueError(f"Invalid engine_type {data['engine_type']}, valid values are `spark` or `dlt`")
        
        # Generate new cron expression if schedule_interval or advanced_scheduling changed
        schedule_interval_changed = "schedule_interval" in data
        advanced_scheduling_changed = "advanced_scheduling" in data
        
        if schedule_interval_changed or advanced_scheduling_changed:
            new_schedule_interval = data.get("schedule_interval", schedule.get("schedule_interval"))
            new_advanced_scheduling = data.get("advanced_scheduling", schedule.get("advanced_scheduling"))
            
            # Generate new cron expression 
            new_cron_expression = self._generate_cron_expression(new_schedule_interval, new_advanced_scheduling)
            if new_cron_expression:
                data["generated_cron_expression"] = new_cron_expression
                logger.info(f"Generated new cron expression for edit: {new_cron_expression}")
        
        # revert formatting from configurations in request
        # if "configurations" in data:
        #     data["configurations"] = self._reverse_format_configuration(data["configurations"])
        
        _, schedule = self.schedule_collection.get_by_id(schedule_id)
        
        # We will skip the edit part for older schedule which do not have required fields
        if schedule.get("meta_schedule_version", 1) == 1:
            if "meta_schedule_version" in data and data["meta_schedule_version"] == 2:
                # this is a update version request, we should proceed
                pass
            else:
                return {
                    "success": False,
                    "msg": "Can not edit older schedules"
                }, 400
        
        # Update MongoDB
        _, result = self.schedule_collection.update_all(schedule_id, data)
        
        _, schedule = self.schedule_collection.get_by_id(schedule_id)
        
        dag_data = {
            "conf": {
                "job_id": schedule.get("chat_id", ""),
                "user_id": schedule.get("user_id", ""),
                "job_name": chat.get("chat_name", ""),
                "schedule_interval": schedule.get("schedule_interval", "once"),
                "advanced_scheduling": schedule.get("advanced_scheduling", {}),
                "helper_module": Config.config["airflow"]["helper_module"],
                "executionType": schedule.get("execution_type", "pipeline"),
                "engine_type": schedule.get("engine_type", "spark"),
                "local": True if schedule.get("type") == "localstorage" else False,
                "dlt_conf": schedule.get("configurations", {}).get("--conf", None),
                "spark_conf": schedule.get("configurations", {}).get("--conf", None),
                "spark_path": Config.config["airflow"]["spark_path"],
                "spark_packages" : packages,
                "schedule_id": schedule_id,
                "schedule_name": schedule.get("schedule_name", ""),
                "notification": schedule.get("notification", {}),
                "generated_cron_expression": schedule.get("generated_cron_expression", ""),
                "service_type": schedule.get("service_mode", "DTS").lower()
            }
        }
        
        
        response = self.call_api(
            RequestType.POST, "/api/v1/dags/rest-trigger/dagRuns", dag_data)
        
        if 'error' in response:
            logger.error("Error editing schedule {schedule_id}")
            return {
                "success": False,
                "msg": "Error editing schedule"
            }, 500
        
        return {
            "success": True,
            "msg": "Successfully updated Schedule",
            "cron_expression": schedule.get("generated_cron_expression")  # Return cron for immediate visibility
        }, 200
