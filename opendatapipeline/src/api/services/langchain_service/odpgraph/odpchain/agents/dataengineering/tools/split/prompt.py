from ..dataframe_supplier.df_suppy import get_head
 
def get_prompt(chat_id, session):
    try:
        
        head_data = get_head(chat_id, session)
        SPLIT_COLUMN_PROMPT = f"Consider this sample data: {head_data}" + """

            This tool is designed to split a specified column into multiple columns based on a delimiter. It takes four parameters: column, destination_columns, delimiter and extra_info.
            The input to this tool will be used to split the specified source column into multiple columns using the specified delimiter.

            The column parameter is required, while destination_columns, delimiter and extra_info are optional.

            The JSON parameters for this tool are as follows: {{

                - column#string#The name of the column to split.
                - destination_columns#list#The list of column names to store the split values (optional).
                - delimiter#string#The delimiter used to split the source column (optional).
                - extra_info#string#Splitting the column data based on the position of the delimiter cannot be done using split.

            }}
            
            Below are several task descriptions along with their respective input examples.
            
            Task: Split "dob" column into "day", "month", and "year" using '-'
            Example Input: {{"column": "dob", "delimiter": "-", "destination_columns": ["day", "month", "year"], "extra_info": null}}
            
            Task: Split "salary_age" column using ':' (no destination_columns specified)
            Example Input: {{"column": "salary_age", "delimiter": ":", "destination_columns": null, "extra_info": null}}
            
            Task: Split "address" column into "street", "city", and "zip" using ','
            Example Input: {{"column": "address", "delimiter": ",", "destination_columns": ["street", "city", "zip"], "extra_info": null}}
            
            Task: Split "name" column into "first_name" and "last_name" using space (' ')
            Example Input: {{"column": "name", "delimiter": " ", "destination_columns": ["first_name", "last_name"], "extra_info": null}}
            
            Task: Split "phone_number" column into "area_code" and "number" using '-'
            Example Input: {{"column": "phone_number", "delimiter": "-", "destination_columns": ["area_code", "number"], "extra_info": null}}
            
            Task: Split "email" column into "username" and "domain" using '@'
            Example Input: {{"column": "email", "delimiter": "@", "destination_columns": ["username", "domain"], "extra_info": null}}

            Task: Split "pincode" column using rightmost delimiter '_'
            Example Input: {{"column": "pincode", "delimiter": "_", "destination_columns": ["area", "pin"], "extra_info": "splitting the data based on delimiter position cannot be done"}}

            You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
            Generate only json parameter and nothing else. Make sure it always has "column" key.
            """
        return SPLIT_COLUMN_PROMPT
    except Exception as e:
        return ""
