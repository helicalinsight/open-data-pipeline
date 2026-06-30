import calendar
from bson import ObjectId
from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from datetime import datetime, timedelta, time
from ....logger.logger import logger, Logger
from pyspark.sql.dataframe import DataFrame
from src.api.services.base.service_parent import ServiceParent
from audit_tracker.record_computation import OPERATION_TO_COMPUTATION_CLASS
from audit_tracker.audit_tracker import AuditDFType


class AuditUsage(ServiceParent):
    """
    Service class for performing operations related to audit events.

    An audit event represents a compute step such as AddColumn, Rename, etc.
    This class manages the audit of these events by saving records in the MongoDB database.
    """

    def __init__(self, session=None):
        """
        Constructor method.
        """
        super().__init__(session)  # ServiceParent handle session logic
        self.audit_runs = MongoFactory(self.client, "audit_runs", session=self.session)
        self.audit_usage = MongoFactory(self.client, "audit_usage", session=self.session)

        self._start_timestamp = None
        self._end_timestamp = None
        self._records_processed = 0
        self._status = False
        self._step_name = ""
        self._custom_record_computation = OPERATION_TO_COMPUTATION_CLASS
        self._rows = 0
        self._cols = 0

    def start(self):
        self._start_timestamp = datetime.now()

    def end(self):
        self._end_timestamp = datetime.now()

    def set_status(self, status):
        self._status = status

    def set_step_name(self, step_name):
        self._step_name = step_name
        
    def _get_default_record_computation(self, new_df, df_type: AuditDFType):
        rows, cols, cost = 0, 0, 0
        if df_type == AuditDFType.PANDAS:
            rows = len(new_df) if isinstance(new_df, dict) else new_df.shape[0]
            cols = 1 if isinstance(new_df, dict) else new_df.shape[1]
            cost = len(new_df) if isinstance(new_df, dict) else new_df.size
        elif df_type == AuditDFType.SPARK:
            rows = len(new_df) if isinstance(new_df, dict) else new_df.count()
            cols = 1 if isinstance(new_df, dict) else len(new_df.columns)
            cost = rows*cols
        else:
            pass
        return rows, cols, cost

    def compute_record_change(self, step_name, old_df, df):
        if old_df is None or df is None:
            self._records_processed = 0
        else:
            if step_name in self._custom_record_computation:
                obj = self._custom_record_computation[step_name].compute(old_df, df)
                self._rows, self._cols, self._records_processed = obj.rows, obj.cols, obj.cost
            else:
                self._rows, self._cols, self._records_processed = self._get_default_record_computation(df, AuditDFType.PANDAS)

    @Logger.generate
    def save_audit_record(self, user_id, chat_id, schedule_id, run_id, execution_type):
        """
        Save the audit record into the MongoDB collection.

        :param user_id: The user ID related to the audit record.
        :param chat_id: The chat ID related to the audit record.
        :param schedule_id: The schedule ID if available, otherwise None for interactive mode.
        :param run_id: The run ID of the execution.
        :param execution_type: The type of execution (code/yaml).
        """
        audit_record = {
            "user_id": user_id,
            "chat_id": chat_id,
            "schedule_id": schedule_id if schedule_id else None,
            "run_id": run_id,
            "execution_type": execution_type,
            "step_name": self._step_name,
            "start_time": self._start_timestamp,
            "end_time": self._end_timestamp,
            "step_cost": self._records_processed,
            "step_status": self._status,
            "rows": self._rows,
            "cols": self._cols,
        }
        try:
            success, audit_id = self.audit_runs.insert_one(audit_record)
            if success:
                logger.info(f"Audit record saved successfully: {str(audit_id)}")
            else:
                logger.error(f"Failed to save audit record: {audit_record}", exc_info=True)
        except Exception as e:
            logger.error(f"Failed to save audit record: {e}: audit_record: {audit_record}" , exc_info=True)

    @Logger.generate
    def get_audit(self, user_id, req_data):
        """
        Retrieve audit records for a specific user based on the provided request data.

        This method builds a query to filter audit records in the `audit_runs` collection
        based on optional parameters such as chat ID, schedule ID, run ID, execution mode,
        and time range defined by start and end timestamps. The results are compiled into a
        list of dictionaries containing relevant audit information.

        Parameters:
            user_id (str): The ID of the user for whom to retrieve audit records.
            req_data (dict): A dictionary containing optional filter parameters:
                - 'chat_id' (str): The chat ID to filter audit records.
                - 'schedule_id' (str): The schedule ID to filter audit records.
                - 'run_id' (str): The run ID to filter audit records.
                - 'mode' (str): The execution mode to filter audit records.
                - 'start_time' (str): The start of the time range for filtering (ISO 8601 format).
                - 'end_time' (str): The end of the time range for filtering (ISO 8601 format).

        Returns:
            tuple: A tuple containing:
                - dict: A dictionary with the key 'Audits' containing a list of audit records.
                - int: An HTTP status code (200 for success).
        """
        try:
            chat_id = req_data.get('chat_id')
            schedule_id = req_data.get('schedule_id')
            run_id = req_data.get('run_id')
            mode = req_data.get('mode')
            start_time = req_data.get('start_time')
            end_time = req_data.get('end_time')

            query = {"user_id": user_id}

            if chat_id:
                query["chat_id"] = chat_id
            if schedule_id:
                query["schedule_id"] = schedule_id
            if run_id:
                query["run_id"] = run_id
            if mode:
                query["execution_type"] = mode

            if start_time and end_time:
                # Ensure timestamps are converted to datetime objects
                start_time_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_time_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                # Filter on the start_time and end_time fields
                query["start_time"] = {'$gte': start_time_dt}
                query["end_time"] = {'$lte': end_time_dt}
            else:
                logger.warning(f"search audit runs called without start_time ({start_time}) and end_time ({end_time})")

            audits = []
            audit_docs = self.audit_runs.find(query)
            aggregated_audits = {}
            lowest_time = datetime.max
            highest_time = datetime.min
            for doc in audit_docs:
                chat_id = doc.get('chat_id')
                schedule_id = doc.get('schedule_id')
                run_id = doc.get('run_id')
                step_cost = doc.get('step_cost', 0)
                step_rows = doc.get('rows', 0)
                step_cols = doc.get('cols', 0)
                run_start_time = doc.get('start_time')
                run_end_time = doc.get('end_time')
                service_type = doc.get('service_type', 'dts')

                if isinstance(run_start_time, datetime) and run_start_time < lowest_time:
                    lowest_time = run_start_time
                if isinstance(run_end_time, datetime) and run_end_time > highest_time:
                    highest_time = run_end_time

                key = (chat_id, schedule_id, run_id, service_type)
                if key not in aggregated_audits:
                    aggregated_audits[key] = {
                        'Chat_id': chat_id,
                        'Schedule_id': schedule_id,
                        'Run_id': run_id,
                        'service_type': service_type,
                        'mode': doc.get('execution_type'),
                        'Total_run_cost': 0,
                        'Total_rows': 0,
                        'Total_cols': 0,
                        'Total_steps': 0,
                        'run_start_time': datetime.max.isoformat(),
                        'run_end_time': datetime.min.isoformat()
                    }
                if isinstance(run_start_time, datetime):
                    if run_start_time < datetime.fromisoformat(aggregated_audits[key]['run_start_time']):
                        aggregated_audits[key]['run_start_time'] = run_start_time.isoformat()
                
                if isinstance(run_end_time, datetime):
                    if run_end_time > datetime.fromisoformat(aggregated_audits[key]['run_end_time']):
                        aggregated_audits[key]['run_end_time'] = run_end_time.isoformat()
                
                if step_cost is not None and isinstance(step_cost, int):
                    aggregated_audits[key]['Total_run_cost'] += step_cost
                    aggregated_audits[key]['Total_rows'] += step_rows
                    aggregated_audits[key]['Total_cols'] += step_cols
                    aggregated_audits[key]['Total_steps'] += 1
                else:
                    logger.warning(f"`step_cost` is invalid for (chat_id, schedule_id, run_id) - {key}")

            # lowest_time_iso = lowest_time.isoformat() if lowest_time != datetime.max else None
            # highest_time_iso = highest_time.isoformat() if highest_time != datetime.min else None

            # for audit in aggregated_audits.values():
            #     audit['run_start_time'] = lowest_time_iso
            #     audit['run_end_time'] = highest_time_iso

            audits = list(aggregated_audits.values())

            return {'Audits': audits}, 200

        except Exception as e:
            logger.error(f"Error in get_audit: {e}, user_id: {user_id}, schedule_id: {schedule_id}, run_id: {run_id}, execution_type: {mode}" , exc_info=True)
            return {"success": False, "msg": "An error occurred during get audit."}, 500
        

    @Logger.generate
    def get_billing_summary(self, user_id, req_data):
        """
        Retrieve the billing summary for a specific user based on the provided request data.

        This method checks if the billing summary already exists in the `audit_usage` collection.
        If the summary exists, it returns the result, otherwise, it queries `audit_runs` 
        to calculate the summary, stores it in `audit_usage`, and then returns the result.

        Parameters:
            user_id (str): The ID of the user for whom to retrieve the billing summary.
            req_data (dict): A dictionary containing filter parameters:
                - 'summary_type' (str): The type of summary (daily, weekly, monthly, yearly).
                - 'target_date' (str): The target date to calculate the summary.

        Returns:
            tuple: A tuple containing:
                - dict: A dictionary with billing summary details.
                - int: An HTTP status code (200 for success).
        """
        try:
            summary_type = req_data.get('summary_type')
            target_date = req_data.get('target_date')

            if not summary_type or not target_date:
                return {"success": False, "msg": "Missing required parameters."}, 400
            summary_type = summary_type.strip().lower()

            try:
                target_date_dt = datetime.strptime(target_date, '%Y-%m-%d')
            except ValueError:
                return {"error": "Invalid date format. Please use YYYY-MM-DD."}, 400

            start_date, end_date = self._get_date_range(target_date_dt, summary_type)

            # Check if a summary already exists
            usage_query = {
                "user_id": user_id,
                "summary_type": summary_type,
                "start_date": start_date
            }
            success, existing_summary = self.audit_usage.get_one_by_query(usage_query)

            if success:
                if '_id' in existing_summary:
                    existing_summary['_id'] = str(existing_summary['_id'])

                for key, value in existing_summary.items():
                    if isinstance(value, datetime):
                        existing_summary[key] = value.isoformat()
                return existing_summary, 200

            # If no existing summary, query audit_runs to generate it
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "start_time": {"$gte": start_date},
                        "end_time": {"$lte": end_date}
                    }
                },
                {
                    "$group": {
                    "_id": {
                        "user_id": "$user_id",
                        # Default to 'dts' if service_type is missing
                        "service_type": {"$ifNull": ["$service_type", "dts"]},
                        **(
                            {
                                "day": {"$dayOfMonth": "$start_time"},
                                "dayWeek": {"$dayOfWeek": "$start_time"}
                            }
                            if summary_type != 'yearly'
                            else {"month": {"$month": "$start_time"}}
                        )
                    },
                    "audit_cost": {"$sum": "$step_cost"},
                    "audit_rows": {"$sum": "$rows"},
                    "audit_cols": {"$sum": "$cols"},
                    "audit_steps": {"$sum": 1}
                    }
                },
                {
                    "$project": {
                        "audit_cost": 1,
                        "audit_rows": 1,
                        "audit_cols": 1,
                        "audit_steps": 1,
                        "_id": 0,
                        "service_type": "$_id.service_type",
                        **(
                            {
                                "day": "$_id.day",
                                "dayWeek": "$_id.dayWeek"
                            }
                            if summary_type != 'yearly'
                            else {"month": "$_id.month"}
                        )
                    }
                }
            ]

            audit_runs = self.audit_runs.aggregate(pipeline)

            total_audit_cost = 0
            total_audit_rows = 0
            total_audit_cols = 0
            total_audit_steps = 0
            details = []
            for run in audit_runs:
                if summary_type == 'yearly':
                    # Handle month-wise detail link
                    month = run['month']
                    month_start_timestamp = datetime(start_date.year, month, 1)
                    _, last_day = calendar.monthrange(start_date.year, month)
                    month_end_timestamp = datetime(start_date.year, month, last_day, 23, 59)
                    
                    start_str = month_start_timestamp.strftime('%Y-%m-%dT%H:%M')
                    end_str = month_end_timestamp.strftime('%Y-%m-%dT%H:%M')

                    detail_link = f"/audit/billing/explore?start_time={start_str}&end_time={end_str}"
                    details.append({
                        "month": month,
                        "audit_cost": run['audit_cost'],
                        "audit_rows": run.get('audit_rows', 0),
                        "audit_cols": run.get('audit_cols', 0),
                        "audit_steps": run.get('audit_steps', 0),
                        "detail_link": detail_link,
                        "service_type": run['service_type']
                    })
                else:
                    day = run['day']
                    if summary_type == "daily":
                        day = 1
                    if summary_type == "weekly":
                        day = run['dayWeek']
                        # Mongo considers Sunday as 1st day of week and names it 1, so we need to adjust accordingly
                        if day == 1: # Sunday
                            day = 7
                        else:
                            day = day - 1 # Monday 1 to Saturday 6

                    day_start_timestamp = start_date + timedelta(days=day - 1) if day > 1 else start_date
                    day_end_timestamp = datetime.combine(day_start_timestamp, time(23, 59))
                    day = run['day']
                    start_str = day_start_timestamp.strftime('%Y-%m-%dT%H:%M')
                    end_str = day_end_timestamp.strftime('%Y-%m-%dT%H:%M')

                    detail_link = f"/audit/billing/explore?start_time={start_str}&end_time={end_str}"
                    details.append({
                        "day": day,
                        "audit_cost": run['audit_cost'],
                        "audit_cost": run['audit_cost'],
                        "audit_rows": run.get('audit_rows', 0),
                        "audit_cols": run.get('audit_cols', 0),
                        "audit_steps": run.get('audit_steps', 0),
                        "detail_link": detail_link,
                        "service_type": run['service_type']
                    })
                try:
                    total_audit_cost += run['audit_cost']
                    total_audit_rows += run.get('audit_rows', 0)
                    total_audit_cols += run.get('audit_cols', 0)
                    total_audit_steps += run.get('audit_steps', 0)
                except Exception as e:
                    logger.error(str(e), exc_info=True)
            # Store the summary in audit_usage
            summary_data = {
                "user_id": user_id,
                "summary_type": summary_type,
                "start_date": start_date.strftime('%Y-%m-%d %H:%M:%S'),
                "end_date": end_date.strftime('%Y-%m-%d %H:%M:%S'),
                "total_audit_cost": total_audit_cost,
                "total_audit_rows": total_audit_rows,
                "total_audit_cols": total_audit_cols,
                "total_audit_steps": total_audit_steps,
                "daily_details": details
            }

            inserted_id = self.audit_usage.insert_document(summary_data)
            summary_data['_id'] = str(inserted_id)
            return summary_data, 200

        except Exception as e:
            logger.error(f"Error in get_billing_summary: {e}, user_id: {user_id}, summary_type: {summary_type}", exc_info=True)
            return {"success": False, "msg": "An error occurred during billing summary retrieval."}, 500
        
    def _get_date_range(self, target_date_dt, summary_type):
        """
        Determines the start_date and end_date based on the target_date and summary_type.
        
        Args:
            target_date_dt (datetime): The target date as a datetime object.
            summary_type (str): The type of summary (daily, weekly, monthly, yearly).

        Returns:
            tuple: (start_date, end_date) as datetime objects.
        
        Raises:
            ValueError: If the summary_type is invalid.
        """
        if summary_type == 'daily':
            start_date = target_date_dt
            end_date = target_date_dt + timedelta(days=1) - timedelta(seconds=1)
        elif summary_type == 'weekly':
            start_date = target_date_dt - timedelta(days=target_date_dt.weekday())
            end_date = start_date + timedelta(days=7)
        elif summary_type == 'monthly':
            start_date = target_date_dt.replace(day=1)
            # Handle the case for year-end (December to January)
            end_date = (start_date.replace(month=start_date.month + 1) if start_date.month < 12
                        else start_date.replace(year=start_date.year + 1, month=1))
        elif summary_type == 'yearly':
            start_date = target_date_dt.replace(month=1, day=1)
            end_date = start_date.replace(year=start_date.year + 1)
        else:
            raise ValueError("Invalid summary type.")
        
        return start_date, end_date