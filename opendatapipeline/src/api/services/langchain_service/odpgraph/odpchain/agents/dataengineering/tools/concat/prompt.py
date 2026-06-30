
from ..dataframe_supplier.df_suppy import get_head
 
def get_prompt(chat_id, session):
    try:
        head_data = get_head(chat_id, session)
        CONCAT_COLUMNS_PROMPT = f"Consider this sample data: {head_data}" + """

            This tool is designed to concatenate multiple columns into a new column. It takes four parameters: columns, separator, destination_column and extra_info.
            The input to this tool will be used to concatenate the specified source columns using the specified separator and store the result in the destination column.

            The columns parameter is required, while separator, destination_column and extra_info are optional.

            The JSON parameters for this tool are as follows: {{

                - columns#list#The list of column names to concatenate.
                - separator#string#The separator to use between concatenated values (optional).
                - destination_column#string#The name of the column to store the concatenated result (optional).
                - extra_info#string#The extra information like concatting multiple columns on multiple separators (optional).

            }}
            
            Below are Just several task descriptions along with their respective input examples do not change the user task based on examples given, These are just for your understanding..
            
            Task: Concatenate "day", "month", and "year" into "dob" using '-'
            Example Input: {{"columns": ["day", "month", "year"], "separator": "-", "destination_column": "dob", "extra_info": null}}
            
            Task: Concatenate "salary" and "age" using ':' (no destination_column specified)
            Example Input: {{"columns": ["salary", "age"], "separator": ":", "destination_column": null, "extra_info": null}}
            
            Task: Concatenate "first_name" and "last_name" using space (' ') into "full_name"
            Example Input: {{"columns": ["first_name", "last_name"], "separator": " ", "destination_column": "full_name", "extra_info": null}}
            
            Task: Concatenate "street", "city", and "zip" using ','
            Example Input: {{"columns": ["street", "city", "zip"], "separator": ",", "destination_column": null, "extra_info": null}}
            
            Task: Concatenate "username" and "domain" using '@' into "email_address"
            Example Input: {{"columns": ["username", "domain"], "separator": "@", "destination_column": "email_address", "extra_info": null}}
            
            Task: Concatenate "prefix" and "phone_number" using '-' into "full_phone_number"
            Example Input: {{"columns": ["prefix", "phone_number"], "separator": "-", "destination_column": "full_phone_number", "extra_info": null}}

            You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
            Generate only json parameter and nothing else. Make sure it always has "columns" key.
            """
        return CONCAT_COLUMNS_PROMPT
    except Exception as e:
        return ""
