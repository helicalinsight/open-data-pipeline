import os
from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
import pandas as pd
logger = Logger

class Write:

    @logger.generate
    def csv(self, dataframe, path, config={}):
        """
        Writes a DataFrame to a CSV file

        :param dataframe: The DataFrame to write to the CSV file
        :param path: The file path of the CSV file to write
        """
        try:
            config_dict = {'header': True}
            mode = config.get("mode", "overwrite")
            config.pop("mode", None)
            config_dict.update(config)
            dataframe.repartition(1).write.mode(mode).options(**config_dict).csv(f"file:///{path}")
            logger.info(f"File saved to path: {path}")
            logger.info("Saved file successfully.")
        except Exception as e:
            logger.error(f"Error during write operation: {str(e)}")
            raise UtilsException("Failed to write to csv.") from e

    @logger.generate
    def xlsx(self, dataframe, path, config={}):
        """
        Writes a Spark DataFrame to an Excel file using Pandas conversion
        
        :param dataframe: The Spark DataFrame to write to the Excel file
        :param path: The file path of the Excel file to write
        :param config: Configuration options for Excel writing
        """
        try:
            logger.info(f"Starting Excel export to: {path}")
            
            # Handle datetime columns in Spark BEFORE conversion to Pandas
            from pyspark.sql.functions import col, date_format
            from pyspark.sql.types import TimestampType, DateType
            
            processed_dataframe = dataframe
            for field in dataframe.schema.fields:
                if isinstance(field.dataType, (TimestampType, DateType)):
                    logger.info(f"Converting datetime column '{field.name}' to string")
                    processed_dataframe = processed_dataframe.withColumn(
                        field.name, 
                        date_format(col(field.name), "yyyy-MM-dd HH:mm:ss")
                    )
            
            # Convert processed Spark DataFrame to Pandas
            pandas_df = processed_dataframe.toPandas()
            logger.info(f"DataFrame converted - Shape: {pandas_df.shape}")
            
            # Ensure absolute path
            if not path.startswith('/'):
                path = f"/{path}"
            
            # Create directory and file path
            os.makedirs(path, exist_ok=True)
            excel_file_path = os.path.join(path, "part-00000.xlsx")
            
            # Write Excel file
            pandas_df.to_excel(excel_file_path, index=False, engine='openpyxl', sheet_name='Sheet1')
            logger.info(f"Excel file written to: {excel_file_path}")
            
            # Create _SUCCESS file
            success_file = os.path.join(path, "_SUCCESS")
            with open(success_file, 'w') as f:
                f.write("")
            
            logger.info("Excel export completed successfully")
            
        except Exception as e:
            logger.error(f"Excel export failed: {str(e)}")
            raise UtilsException("Failed to write to excel.") from e


    @logger.generate
    def json(self, dataframe, path, config={}):
        """
        Writes a DataFrame to a JSON file
        
        :param dataframe: The DataFrame to write to the JSON file
        :param path: The file path of the JSON file to write
        :param config: Configuration options for JSON writing
        """
        try:
            mode = config.get("mode", "overwrite")
            config.pop("mode", None)
            
            # Remove any remaining config options that don't apply to JSON
            json_config = {k: v for k, v in config.items() if k in ['compression', 'dateFormat', 'timestampFormat']}
            
            dataframe.repartition(1).write.mode(mode).options(**json_config).json(f"file:///{path}")
            logger.debug(f"File saved to path: {path}")
            logger.info("Saved JSON file successfully.")
        except Exception as e:
            logger.error(f"Error during JSON write operation: {str(e)}")
            raise UtilsException("Failed to write to json.") from e
