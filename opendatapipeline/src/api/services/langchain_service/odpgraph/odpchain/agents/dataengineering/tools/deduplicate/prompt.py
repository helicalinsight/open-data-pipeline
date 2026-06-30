
from ..dataframe_supplier.df_suppy import get_head
 
def get_prompt(chat_id, session):
    try:
        head_data = get_head(chat_id, session)
        DEDUPLICATE_COLUMNS_PROMPT = f"Consider this sample data: {head_data}" + """

            This tool is designed to deduplicate values in one or more columns. It takes two parameters: columns and extra_info.
            The input to this tool will be used to remove duplicate values from the specified columns.

            The columns parameter is required, while the extra_info parameter is optional. If no extra_info value is provided, it will default to None.

            The JSON parameters for this tool are as follows: {{

                - columns#list#The list of column names to be deduplicated.
                - extra_info#string#The extra information contains the information like cannot be performed on rows.

            }}
            
            Below are several task descriptions along with their respective input examples.
            
            Task: Deduplicate values in "day", "month", and "year" columns
            Example Input: {{"columns": ["day", "month", "year"], "extra_info": null}}
            
            Task: Remove duplicates from "salary" and "age" columns
            Example Input: {{"columns": ["salary", "age"], "extra_info": null}}
            
            Task: Deduplicate values in "name" column
            Example Input: {{"columns": ["name"], "extra_info": null}}
            
            Task: Remove duplicates from "email" column
            Example Input: {{"columns": ["email"], "extra_info": null}}
            
            Task: Deduplicate values in "phone_number" column
            Example Input: {{"columns": ["phone_number"], "extra_info": null}}
            
            Task: Remove duplicates from "department" column
            Example Input: {{"columns": ["department"], "extra_info": null}}
            
            Task: Remove duplicates from rows
            Example Input: {{"columns": [""], "extra_info": "Cannot remove deduplicates from row"}}

            You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
            Generate only json parameter and nothing else. Make sure it always has "columns" key.
            """
        return DEDUPLICATE_COLUMNS_PROMPT
    except Exception as e:
        return ""
