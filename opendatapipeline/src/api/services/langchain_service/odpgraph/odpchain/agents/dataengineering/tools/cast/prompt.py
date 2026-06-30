from ..dataframe_supplier.df_suppy import get_head

def get_prompt(chat_id, session):
    try:
        head_data = get_head(chat_id, session)
        CAST_COLUMN_PROMPT = f"Consider this sample data: {head_data}" + """

        This tool is designed to cast a specified column in a dataset to a new data type. It takes four parameters: columns, new_type, old_type and extra_info.
        The input to this tool will be used to cast the specified column to the new data type with an optional old_type and extra_info values.

        Both columns and new_type parameters are required, while old_type and extra_info are optional. If no old_type value is provided, it will default to None. If no extra_info value is provided, it will default to None.

        The JSON parameters for this tool are as follows: {{

            - columns#string#The name of the column to be cast.
            - new_type#string#The new data type to cast the column to.
            - old_type#string#The old data type of the column, if applicable.
            - extra_info#string#The extra information like casting cannot be on all the columns at once.

        }}     
    
        
        Below are several task descriptions along with their respective input examples.
        
        Task: Cast the "age" column to integer
        Example Input: {{"columns": "age", "old_type": null, "new_type": "integer", "extra_info": null}}
        
        Task: Cast the "identity" column to string
        Example Input: {{"columns": "identity", "old_type": null, "new_type": "string", "extra_info": null}}
        
        Task: Cast the "identity" column to object
        Example Input: {{"columns": "identity", "old_type": null, "new_type": "object", "extra_info": null}}
        
        Task: Cast the "dob" column from Unix timestamp to date
        Example Input: {{"columns": "dob", "old_type": "unix", "new_type": "date", "extra_info": null}}
        
        Task: Cast the "datelogsTesting" column from mmddyyy format to date
        Example Input: {{"columns": "datelogsTesting", "old_type": "mmddyyy", "new_type": "date", "extra_info": null}}
        
        Task: Change the "startdateTesting" column from mdy format to date
        Example Input: {{"columns": "startdateTesting", "old_type": "mdy", "new_type": "date", "extra_info": null}}
        
        Task: Change the "end_dateTesting" column from ddmmyyyy format to date
        Example Input: {{"columns": "end_dateTesting", "old_type": "ddmmyyyy", "new_type": "date", "extra_info": null}}
        
        Task: Convert the "salary" column from float to integer
        Example Input: {{"columns": "salary", "old_type": "float", "new_type": "integer", "extra_info": null}}
        
        Task: Cast the "phone_number" column from string to integer
        Example Input: {{"columns": "phone_number", "old_type": "string", "new_type": "integer", "extra_info": null}}
        
        Task: cast the origin_etd column to date from dd-MMM-yy using casting
        Example Input: {{"columns": "origin_etd", "old_type": "dd-MMM-yy", "new_type": "date", "extra_info": null}}
        
        Task: cast dob to date
        Example Input: {{"columns": "dob", "old_type": null, "new_type": "date", "extra_info": null}}
        
        Task: cast dob to date using mm-dd-yyyy
        Example Input: {{"columns": "dob", "old_type": "mm-dd-yyyy", "new_type": "date", "extra_info": null}}
        
        Task: cast all columns to string
        Example Input: {{"columns": "*", "old_type": null, "new_type": "string", "extra_info": "cannot cast all columns"}}
        
        """  
        

        return CAST_COLUMN_PROMPT
    except Exception as e:
        return ""
