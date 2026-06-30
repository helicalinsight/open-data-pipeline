
from ..dataframe_supplier.df_suppy import get_head
 
def get_prompt(chat_id, session):
    try:
        head_data = get_head(chat_id, session)
        DATE_FORMAT_TOOL_PROMPT = f"Consider this sample data: {head_data}" + """

            This tool enables users to update the format of dates in a specified column to a new format.
            It facilitates the conversion of date formats to align with specific requirements.
            It takes three parameters: columns, format and extra_info.
            
            The columns and format parameters are required, while the extra_info parameter is optional. If no extra_info value is provided, it will default to None.

            The JSON parameters for this tool are as follows: {{

                - columns#str#Name of the column containing dates.
                - format#str#New format for the dates.
                - extra_info#string#The extra information like date format cannot be performed on columns which are not of type date
            
            }}

            Below are a few task descriptions along with their respective input examples:
            
            Task: Format exam_date to MMM d, yyyy.
            Example Input: {{"columns": "exam_date", "format": "MMM d, yyyy", "extra_info": null}}
            
            Task: Convert birth_date format to dd-mm-yyyy.
            Example Input: {{"columns": "birth_date", "format": "dd-mm-yyyy", "extra_info": null}}
            
            Task: Convert test to yyyy-mm-dd.
            Example Input: {{"columns": "test", "format": "yyyy-mm-dd", "extra_info": "Column is not of type date"}}
            
            You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
            Generate only json parameter and nothing else. Make sure it always has "columns" and "format" keys.
        """
        return DATE_FORMAT_TOOL_PROMPT
    except Exception as e:
        return ""
