from ..logger.logger import Logger, logger
from .dataframes import Dataframes
from .processor import Processor
from ..exceptions.exceptions import *
dataframe = Dataframes()

logger = Logger

class Manager:
    def __init__(self, pipeline, connection_id, config, spark,schedule_conf):
        self.pipeline = pipeline # chat history object
        self.connection_id = connection_id # connection id dictionary; contains details for all connections for the job
        self.config = config # schedule configurations; 'configurations' section from document in schedule collection
        self.spark = spark # spark session context
        self.schedule_conf=schedule_conf # schedule details

    @logger.generate
    def manage(self):
        try:
            pipeline = self.pipeline
            connection_id = self.connection_id
            config = self.config
            # pipeline = self.sort_pipeline(pipeline)
            pipeline_processor = Processor()
            pipeline_processor.process(pipeline, connection_id, self.spark, self.schedule_conf, config)
            logger.info("Pipeline processed successfully.")
        except Exception as e:
            logger.error(f"Operation 'manage' executed with an exception: pipeline :{pipeline}, connection_id :{connection_id} and config :{config}")
            raise ManagerException("Failed to process the data.") from e

    @logger.generate
    def sort_pipeline(self, unsorted_pipeline):
        try:
            logger.info("sorting pipeline..")
            # Putting ReadFiles or ReadTables steps first in the pipeline
            read_steps = [step for step in unsorted_pipeline if step['function'] == 'read_files' or step['function']
                        == 'read_tables' or step['function'] == 'read']
            # Putting Export or ExportTables steps last in the pipeline
            export_steps = [step for step in unsorted_pipeline if step['function'] == 'export' or step['function'] ==
                            'export_table']
            other_steps = [step for step in unsorted_pipeline if step['function'] not in ['read_files', 'read_tables',
                                                                                        'export', 'export_table', 'read']]
            pipeline_sorted = read_steps + other_steps + export_steps
            logger.info(f"pipeline sorted: {pipeline_sorted}")
            return pipeline_sorted
        except Exception as e:
            logger.error(f"Failed to sort the pipeline: unsorted_pipeline :{unsorted_pipeline}")
            raise ManagerException("Failed to sort pipeline.") from e
