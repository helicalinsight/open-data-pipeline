import enum
from datetime import datetime
from dataclasses import dataclass
import functools
from audit_tracker.record_computation import OPERATION_TO_COMPUTATION_CLASS
from typing import Optional

class AuditDFType(enum.Enum):
    """
    Enum for the type of dataframe.
    """
    PANDAS = "pandas"
    SPARK = "spark"
    
@dataclass
class ScheduleRunContext:
    user_id: str
    chat_id: str
    schedule_id: str
    run_id: str
    execution_type: str
    service_type: str = "dts"

class AuditTracker:
    """
    Common audit tracker class for all the audit events.
    """
    def __init__(self, audit_runs_collection, audit_usage_collection, run_context: ScheduleRunContext):
        self.audit_runs_collection = audit_runs_collection
        self.audit_usage_collection = audit_usage_collection
        self._start_timestamp = None
        self._end_timestamp = None
        self._records_processed = 0
        self._status = False
        self._step_name = ""
        self._rows = 0
        self._cols = 0
        self._run_context = run_context
        
    def custom_record_computation(self, _: AuditDFType = None) -> dict:
        """
        Custom record computation for the audit event.
        """
        return OPERATION_TO_COMPUTATION_CLASS
    
    def start(self):
        self._start_timestamp = datetime.now()

    def end(self):
        self._end_timestamp = datetime.now()

    def set_status(self, status):
        self._status = status

    def set_step_name(self, step_name):
        self._step_name = step_name
        
    @staticmethod
    def echo_function(rows: int, cols: int):
        """
        This is a utility function that can be passed to record custom changes in audit. 
        If after performing an operation, caller of this function has access to number of rows and columns changed, they can use this function to use when calling "record" wrapper
        """
        return {
            "rows": rows,
            "cols": cols
        }
        
    def _get_default_record_computation(self, new_df, df_type: AuditDFType = None):
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
            # This function can also accept a dictionary with "rows" and "cols" keys
            if "rows" in new_df and "cols" in new_df:
                rows = new_df["rows"]
                cols = new_df["cols"]
                cost = rows*cols
        return rows, cols, cost

    def compute_record_change(self, step_name, old_df, new_df, df_type: AuditDFType = None):
        if old_df is None and new_df is None:
            self._records_processed = 0
        else:
            if step_name in self.custom_record_computation():
                obj = self.custom_record_computation()[step_name].compute(old_df, new_df)
                self._rows, self._cols, self._records_processed = obj.rows, obj.cols, obj.cost
            else:
                self._rows, self._cols, self._records_processed = self._get_default_record_computation(new_df, df_type)

    def save_audit_record(self, user_id, chat_id, schedule_id, run_id, execution_type, service_type = "dts"):
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
            "service_type": service_type,
            "step_name": self._step_name,
            "start_time": self._start_timestamp,
            "end_time": self._end_timestamp,
            "step_cost": self._records_processed,
            "step_status": self._status,
            "rows": self._rows,
            "cols": self._cols,
        }
        try:
            success, audit_id = self.audit_runs_collection.insert_one(audit_record)
        except Exception as e:
            pass
        
    def track_audit_event(
            self, old_df, new_df, step_name, df_type, start_time, end_time
        ):
        self.set_step_name(step_name)
        self._start_timestamp = start_time
        self._end_timestamp = end_time
        self.compute_record_change(step_name, old_df, new_df, df_type)
        
        self.save_audit_record(
            self._run_context.user_id,
            self._run_context.chat_id,
            self._run_context.schedule_id,
            self._run_context.run_id,
            self._run_context.execution_type,
            self._run_context.service_type
        )

    def record(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            To be called as,
            audit_tracker.record(spark.read.jdbc)(url=jdbc_url, table=f"({sql_query})", 
                properties=properties, step_name='read', old_df=None
            )
            """
            old_df = kwargs.pop('old_df') if 'old_df' in kwargs else None
            step_name = kwargs.pop('step_name') if 'step_name' in kwargs else 'manual'
            audit_df_type: Optional[AuditDFType] = kwargs.pop('audit_df_type', None)  # default to spark
            self.start()
            self.set_step_name(step_name)
            new_df = func(*args, **kwargs)
            self.end()
            self.compute_record_change(step_name, old_df, new_df, audit_df_type)
            
            self.save_audit_record(
                self._run_context.user_id,
                self._run_context.chat_id,
                self._run_context.schedule_id,
                self._run_context.run_id,
                self._run_context.execution_type,
                self._run_context.service_type
            )
            return new_df

        return wrapper
