'''
This module is used to create a Spark dataframe for the AOD code.

This class takes optional spark dataframe for initialization
'''
from typing import Optional
from pyspark.sql import DataFrame
from audit_tracker.audit_tracker import AuditTracker
from datetime import datetime

class AodSparkFrame:
    
    def __init__(
            self, df, audit_tracker
        ):
        self._df: DataFrame = df
        self.audit_tracker: AuditTracker = audit_tracker

    def write_csv(self, path: str, **kwargs):
        """
        Write the Spark DataFrame to a CSV file and emit an audit event.

        :param path: The file path to write the CSV to.
        :param kwargs: Additional options for Spark's DataFrameWriter.csv().
        """
        _start = datetime.now()
        self._df.write.options(**kwargs).csv(path)
        _end = datetime.now()
        self.audit_tracker.track_audit_event(
            self._df,  # old_df (could be None, but for write, passing current df)
            None,      # new_df (None, since we're writing out)
            'write',
            AuditTracker.AuditDFType.SPARK if hasattr(AuditTracker, 'AuditDFType') else 'spark',
            _start,
            _end
        )
