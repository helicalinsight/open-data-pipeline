import json
import pandas as pd

from ..transformations_utilities.utilities import TransformerUtilities
from ....exceptions.exception import *
from ....logger.logger import Logger, logger
import base64
util = TransformerUtilities()


class DataSummary:
    """
    This class generates a data summary for the given DataFrame and includes a method for previewing the file

    """
    @Logger.generate
    def file_preview(self, dataframe, id, alias):
        """
        Generates a dictionary with detailed information about the given DataFrame, including '_id', alias, total number of records, total number of records in the DataFrame, column information, and data, and returns this dictionary
        
        :param dataframe: The Pandas DataFrame to be converted to JSON.
        :type dataframe: pandas.DataFrame
        :param id: The unique identifier of the file.
        :type id: str
        :param alias: The alias or name associated with the file.
        :type alias: str
        :return: A boolean indicating success or failure, Generated file preview dictionary
        :rtype: bool, dict
        """
        logger.info("Preview in manager is called.")
        file_preview = []
        try:
            # Note: Following line is replacing empty string and NaN values with None. This is not needed and hence commented.
            # dataframe = dataframe.replace(r'^\s*$', None, regex=True).where(pd.notnull(dataframe), None)
            
            columns_info = util.get_column_datatype_dict(dataframe)
            for col in dataframe.columns:
                if pd.api.types.is_datetime64_any_dtype(dataframe[col]):
                    dataframe[col] = dataframe[col].astype(str)
                    
            binary_columns = [col for col in dataframe.columns if dataframe[col].apply(lambda x: isinstance(x, bytes)).any()]
            for col in binary_columns:
                dataframe[col] = dataframe[col].apply(lambda x: base64.b64encode(x).decode('utf-8') if isinstance(x, bytes) else x)

            json_df = dataframe.to_json(orient='records')

            data = json.loads(json_df)

            file_preview.append({
                "_id": str(id),
                "alias": alias,
                "total_records": len(data),
                "total_records_dataframe": len(dataframe),
                "columns": columns_info,
                "data": data
            })
            logger.info(f"Returning file_info")
            return True, file_preview
        except Exception as e: # pragma: no cover
            logger.error(f"Failed to preview the file: {str(e)}", exc_info=True)
            raise PreviewException("Failed to preview the data.") from e
