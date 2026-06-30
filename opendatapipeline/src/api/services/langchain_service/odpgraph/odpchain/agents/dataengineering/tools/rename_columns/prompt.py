from ..dataframe_supplier.df_suppy import get_columns
from ..........logger.logger import logger, Logger

def get_prompt(chat_id, session):
    try:
        columns_data = get_columns(chat_id, session)
        RENAME_COLUMN_PROMPT = f"Consider this schema: {columns_data}" + """
            
            This tool is designed to rename columns in a dataset. It takes three parameters: old_name, new_name and extra_info.
            The input to this tool will be passed into the column renaming function with extra_info value.

            Both old_name and new_name parameters are required, while the extra_info parameter is optional. If no extra_info value is provided, it will default to None.

            The JSON parameters for this tool are as follows: {{

                - old_name#string#The name of the column to be renamed.
                - new_name#string#The new name for the column.
                - extra_info#string#The extra information like when the old_name column does not exist.

            }}
            
            Below are several task descriptions along with their respective input examples.
            
            Task: Rename age column to age_2
            Example Input: {{"old_name": "age", "new_name": "age_2", "extra_info": null}}
            
            Task: Rename "identity" column to "studentIdentity"
            Example Input: {{"old_name": "identity", "new_name": "studentIdentity", "extra_info": null}}
            
            Task: Rename salary column to monthlySalary
            Example Input: {{"old_name": "salary", "new_name": "monthlySalary", "extra_info": null}}
            
            Task: I like to rename address column to fullAddress
            Example Input: {{"old_name": "address", "new_name": "fullAddress", "extra_info": null}}
            
            Task: Please Rename phone to contactNumber
            Example Input: {{"old_name": "phone", "new_name": "contactNumber", "extra_info": null}}
            
            Task: Rename department to dept
            Example Input: {{"old_name": "department", "new_name": "dept", "extra_info": null}}
            
            Task: Rename test to test1
            Example Input: {{"old_name": "test", "new_name": "test1", "extra_info": "The column to be renamed does not exist"}}

            You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
            Generate only json parameter and nothing else. Make sure it always has "old_name" and "new_name" keys.
            """
        return RENAME_COLUMN_PROMPT
    except Exception as e:
        return ""
