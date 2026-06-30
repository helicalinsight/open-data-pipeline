import pyspark
from ..models.connector import MongoConnector
from core.mongo.mongo_factory import MongoFactory
from datetime import datetime
from ..logger.logger import logger, Logger
from audit_tracker.record_computation import OPERATION_TO_COMPUTATION_CLASS
from audit_tracker.audit_tracker import AuditDFType


class AuditUsage:
    """
    Service class for performing operations related to audit events.

    An audit event represents a compute step such as AddColumn, Rename, etc.
    This class manages the audit of these events by saving records in the MongoDB database.
    """

    def __init__(self):
        """
        Constructor method.
        """
        self.mongo_connector = MongoConnector()
        self.mongo_client = self.mongo_connector.client
        self.session = self.mongo_client._Database__client.start_session()
        self.audit_runs = MongoFactory(self.mongo_client, "audit_runs")
        self.audit_usage = MongoFactory(self.mongo_client, "audit_usage")
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

    def compute_record_change(self, step_name, old_df, new_df):
        if old_df is None or new_df is None:
            self._records_processed = 0
        else:
            if step_name in self._custom_record_computation:
                obj = self._custom_record_computation[step_name].compute(old_df, new_df)
                self._rows, self.cols, self._records_processed = obj.rows, obj.cols, obj.cost
            else:
                self._rows, self._cols, self._records_processed = self._get_default_record_computation(new_df, AuditDFType.PANDAS)

    def process_audit_record(self, audit_record):
        """
        Processes the audit record for serialization.

        Args:
            audit_record (dict): The audit record to be processed.
        """
        if 'step_cost' in audit_record and isinstance(audit_record['step_cost'], dict):
            for step_id, step_info in audit_record['step_cost'].items():
                if 'df' in step_info and isinstance(step_info['df'], pyspark.sql.dataframe.DataFrame):
                    # Convert the PySpark DataFrame to a list of dictionaries
                    audit_record['step_cost'][step_id]['df'] = step_info['df'].toPandas().to_dict(orient='records')
        return audit_record

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
                logger.error(f"Failed to save audit record: {audit_record}")
        except Exception as e:
            logger.error(f"Failed to save audit record: {e}, audit record: {audit_record}")
