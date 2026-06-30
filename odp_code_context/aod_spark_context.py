'''
This module is used to create a Spark context for the AOD code.

This class takes a spark context object as initialization argument. Additionaly, it 
requires a audit_tracker object as initialization argument.

This class has the following methods:
- read_csv: reads a csv file into a AodSparkFrame object.
'''

import pyspark
import pyspark.sql
from audit_tracker.audit_tracker import AuditTracker, AuditDFType
from .aod_spark_frame import AodSparkFrame
from datetime import datetime

class AodSparkContext:
    '''
    This class is used to create a Spark context for the AOD code.
    '''
    def __init__(
        self,
        spark_session: pyspark.sql.SparkSession,
        audit_tracker: AuditTracker
    ):
        self.spark_session = spark_session
        self.audit_tracker = audit_tracker
    
    def read_csv(self, path: str, **kwargs) -> AodSparkFrame:
        _start = datetime.now()
        df = self.spark_session.read.options(**kwargs).csv(path)
        _end = datetime.now()
        self.audit_tracker.track_audit_event(
            None, df, 'read',
            AuditDFType.SPARK,
            _start,
            _end
        )
        return AodSparkFrame(df, self.audit_tracker)
