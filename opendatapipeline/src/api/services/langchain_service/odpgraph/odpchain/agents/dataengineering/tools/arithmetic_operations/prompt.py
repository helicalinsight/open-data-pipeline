
from ..dataframe_supplier.df_suppy import get_head
 
def get_prompt(chat_id, session):
    try:
        head_data = get_head(chat_id, session)
        ARITHMETIC_OPERATIONS_PROMPT = f"Consider this sample data: {head_data}" + """

            This tool enables users to execute arithmetic expressions on data in a dataframe. It takes three parameters: query, destination_column and extra_info.
            It allows for performing arithmetic operations based on the query and storing the result in a new column destination_column.
            
            The query parameter is required, while the destination_column and extra_info parameters are optional. If no destination_column value is provided, it will default to None. If no extra_info value is provided, it will default to None.

            The JSON parameters for this tool are as follows: {{

                - query#string#Expression that we want to apply on the data.
                - destination_column#string#Name of the new column in which we want to store the segregated data.
                - extra_info#string#The extra information like arithmetic operations cannot be performed on non-numeric datatypes.
        
            }}

            Below are several task just as example inputs do not consider them as your task these are just for you to understand how arithmetic_operations task should be done , here is the descriptions along with their respective input examples.
            
            Task: Calculate units_sold + 5 and store it in units_total.
            Example Input: {{"query": "units_sold + 5", "destination_column": "units_total", "extra_info": null}}
            
            Task: Perform units_sold - unit_price and add in units_lost.
            Example Input: {{"query": "units_sold - unit_price", "destination_column": "units_lost", "extra_info": null}}
            
            Task: Do unit_price ** 3.
            Example Input: {{"query": "unit_price ** 3", "destination_column": null, "extra_info": null}}
            
            Task: calculate 1+20-3/10
            Example Input: {{"query": "1+20-3/10", "destination_column": null, "extra_info": null}}
            
            Task: calculate 2 multiply 5
            Example Input: {{"query": "2*5", "destination_column": null, "extra_info": null}}

            Task: add new column profit
            Example Input: {{"query": "new_column", "destination_column": "profit", "extra_info": "to add new column, refer add_columns"}}
            
            Task: calculate ship_date - order_date in days
            Example Input: {{"query": "ship_date - order_date", "destination_column": "days_difference", "extra_info": "date difference in days cannot be calculated"}}

            Note: The tool will execute the provided arithmetic expression on the data. If a new column is provided, the result will be stored in that column.
            
            You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
            Generate only json parameter and nothing else. Make sure it always has "query" key.
            """

        return ARITHMETIC_OPERATIONS_PROMPT
    except Exception as e:
        return ""
