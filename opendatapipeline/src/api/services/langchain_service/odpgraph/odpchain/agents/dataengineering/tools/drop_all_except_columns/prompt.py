
from ..dataframe_supplier.df_suppy import get_columns
 
def get_prompt(chat_id, session):
    try:
        columns_data = get_columns(chat_id, session)
        DROP_ALL_COLUMNS_EXCEPT_PROMPT = f"Consider this schema: {columns_data}" + """

            This tool is designed to drop all columns from a dataset except the ones specified in a list of column names. It takes two parameters: columns and extra_info.
            The input to this tool will be used to determine which columns to keep and drop from the dataset.

            The columns parameter is required, while the extra_info parameter is optional. If no extra_info value is provided, it will default to None.

            The JSON parameters for this tool are as follows: {{

                - columns#list#The list of column names to be kept while dropping all other columns from the dataset.
                - extra_info#string#The extra information contains the information which cannot be achieved using drop all columns except like dropping all columns

            }}

            Below are several task descriptions along with their respective input examples.
            
            Task: Drop all columns except "age", "identity", and "halicate" from the data
            Example Input: {{"columns": ["age", "identity", "halicate"], "extra_info": null}}
            
            Task: Drop all columns except "sample" and "identity" from the data
            Example Input: {{"columns": ["sample", "identity"], "extra_info": null}}
            
            Task: Keep only the "name" and "description" columns, drop all others
            Example Input: {{"columns": ["name", "description"], "extra_info": null}}
            
            Task: Drop all columns except the "code" column
            Example Input: {{"columns": ["code"], "extra_info": null}}
            
            Task: Keep only the "address" and "phone" columns, drop all others
            Example Input: {{"columns": ["address", "phone"], "extra_info": null}}
            
            Task: Drop all columns except the "department" and "email" columns
            Example Input: {{"columns": ["department", "email"], "extra_info": null}}
            
            Task: Drop all columns
            Example Input: {{"columns": [], "extra_info": "cannot drop all columns using drop_all_columns_except"}}
            
            You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
            Generate only json parameter and nothing else. Make sure it always has "columns" key.
            """
        return DROP_ALL_COLUMNS_EXCEPT_PROMPT
    except Exception as e:
        return ""
