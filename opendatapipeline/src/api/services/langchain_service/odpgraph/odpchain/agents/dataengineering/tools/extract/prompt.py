
from ..dataframe_supplier.df_suppy import get_head
 
def get_prompt(chat_id, session):
    try:
        head_data = get_head(chat_id, session)
        EXTRACT_PROMPT = f"Consider this sample data: {head_data}" + """
        
            This tool facilitates the extraction of specific date components from a date column in a dataframe.
            It allows users to extract date components such as year, month, or day and store them in a new column.
            It takes four parameters: column, component, destination_column and extra_info.

            The column and component parameters are required, while the destination_column and extra_info parameters are optional. If no destination_column value is provided, it will default to concatenated string of column parameter and component parameter separated by underscore. If no extra_info value is provided, it will default to None.

            The JSON parameters required for this tool are as follows: {{

                - column#string#The name of the date column from which date components are to be extracted from.
                - component#list#The date component which the user wants to extract from the date column.
                - destination_column#string#The name of the column in which the user wants to store the extracted date component.
                - extra_info#string#The extra information can be anything other than extracting year, month and day.
            
            }}
            
            Below are a few task descriptions along with their respective input examples:
            
            Task: Extract "year" component from "joining_date" column and store it in "joining_year" destination column.
            Example Input: {{"column": "joining_date", "component": ["year"], "destination_column": "joining_year", "extra_info": null}}
            
            Task: Extract day component from birth_date column and store it in bdate destination column.
            Example Input: {{"column": "birth_date", "component": ["day"], "destination_column": "bdate", "extra_info": null}}
            
            Task: Take month date part from current_date column.
            Example Input: {{"column": "current_date", "component": ["month"], "destination_column": null, "extra_info": null}}
            
            Task: Take month year date part from current_date column.
            Example Input: {{"column": "current_date", "component": ["month","year"], "destination_column": null, "extra_info": null}}
            
            Task: Extract the year, month and day column from the testing_column.
            Example Input: {{"column": "testing_column", "component": ["month","year","day"], "destination_column": null, "extra_info": null}}
            
            Task: Calculate the number of days between the `order_date` and `ship_date`.
            Example Input: {{"column": "", "component": ["-"], "destination_column": null, "extra_info": "to calculate the number of days, we need to subtract order_date - shipdate"}}
            
            Task: Extract week number from my_date column
            Example Input: {{"column": "my_date", "component": ["week"], "destination_column": null, "extra_info": "extract only extracts day, month and year"}}
            
            You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
            Generate only json parameter and nothing else. Make sure it always has "columns" and "component" keys.
        """
        return EXTRACT_PROMPT
    except Exception as e:
        return ""
