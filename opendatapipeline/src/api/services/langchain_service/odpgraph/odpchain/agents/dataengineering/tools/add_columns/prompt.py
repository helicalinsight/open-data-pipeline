
from ..dataframe_supplier.df_suppy import get_head

def get_prompt(chat_id, session):
    try:
        head_data = get_head(chat_id, session)
        ADD_COLUMN_PROMPT = f"Consider this sample data: {head_data}" + """

            This tool is designed to add a new column to a dataset. It takes three parameters: columns, default and extra_info. 
            The input to this tool will be used to add the specified column with an optional default and extra_info values.

            The columns parameter is required, while the default and extra_info parameters are optional. If no default value is provided, it will default to None. If no extra_info value is provided, it will default to None.

            The JSON parameters for this tool are as follows: {{

                - columns#string#The name of the column to be added.
                - default#string#The default value to populate the new column with (optional, defaults to None).
                - extra_info#string#The extra information like calculation is required, reference of column, some information to be derived etc.

            }}
            
            Below are several task just as example inputs do not consider them as your task these are just for you to understand how add_columns task should be done , here is the descriptions along with their respective input examples.
            
            Task: Add "age" column to the data
            Example Input: {{"columns": "age", "default": null, "extra_info": null}}
            
            Task: Add a column named "sampleIdentity" to the data with default value as "sample data"
            Example Input: {{"columns": "sampleIdentity", "default": "sample data", "extra_info": null}}
            
            Task: Add "department" column with no default value
            Example Input: {{"columns": "department", "default": null, "extra_info": null}}
            
            Task: Add "email" column with default value as "N/A"
            Example Input: {{"columns": "email", "default": "N/A", "extra_info": null}}
            
            Task: Add "status" column with default value as "active"
            Example Input: {{"columns": "status", "default": "active", "extra_info": null}}
            
            Task: Add "phone" column with no default value
            Example Input: {{"columns": "phone", "default": null, "extra_info": null}}
            
            Task: Add a new column called "profit" which is revenue - cost
            Example Input: {{"columns": "profit", "default": "revenue - cost", "extra_info": "column revenue and cost are required to get the default"}}

            Task: Duplicate "cost" column
            Example Input: {{"columns": "cost", "default": "cost", "extra_info": "column cost is required to get the default value"}}
            
            Task: add new column with current timestamp as value
            Example Input: {{"columns": "current_timestamp", "default": "", "extra_info": "Requires to set the current timestamp at the time of the operation."}}
            
            You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
            Generate only json parameter and nothing else. Make sure it always has "columns" key.
            """
        return ADD_COLUMN_PROMPT
    except Exception as e:
        return ""
        
    
    
agent_prompt="""Answer the following questions as best you can. You have access to the following tools:

add_columns: 
    This tool is designed to add a new column to a dataset. It takes two parameters: column and default. 
    The input to this tool will be used to add the specified column with an optional default value.

    The column parameter is required, while the default parameter is optional. If no default value is provided, it will default to None.

    The JSON parameters for this tool are as follows: {{

        - column#string#The name of the column to be added.
        - default#string#The default value to populate the new column with (optional, defaults to None).

    }}

    Below are several task descriptions along with their respective input examples.
    
    Task: Add "age" column to the data
    Example Input: {{"columns": "age", "default": null}}
    
    Task: Add a column named "sampleIdentity" to the data with default value as "sample data"
    Example Input: {{"columns": "sampleIdentity", "default": "sample data"}}
    
    Task: Add "department" column with no default value
    Example Input: {{"columns": "department"}}
    
    Task: Add "email" column with default value as "N/A"
    Example Input: {{"columns": "email", "default": "N/A"}}
    
    Task: Add "status" column with default value as "active"
    Example Input: {{"columns": "status", "default": "active"}}
    
    Task: Add "phone" column with no default value
    Example Input: {{"columns": "phone"}}
    

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [add_columns]
Action Input: the input to the action
Observation: the result of the action
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""