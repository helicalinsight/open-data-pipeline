from ..dataframe_supplier.df_suppy import get_head
 
def get_prompt(chat_id, session):
    try:
        head_data = get_head(chat_id, session)
        TRIM_COLUMN_PROMPT = f"Consider this sample data: {head_data}" + """

            This tool is designed to trim a specified number of characters from a column in a dataset. It takes four parameters: number_of_characters, location, columns and extra_info. 
            The input to this tool will be used to trim the specified number of characters from the specified location in the given column.

            The columns parameter is required, while the number_of_characters, location and extra_info parameters are optional. If no number_of_characters value is provided, it will default to 1. If no location value is provided, it will default to 'left'. If no extra_info value is provided, it will default to None.

            The JSON parameters for this tool are as follows: {{

                - number_of_characters#integer#The number of characters to trim from the specified location. Default: 1.
                - location#string#The location to perform trimming. Can be 'left' or 'right'. Default: 'left'.
                - columns#string#The column in the dataset to apply the trimming operation.
                - extra_info#string#The extra information like when the column specified does not exist

            }}
            
            Below are several task descriptions along with their respective input examples.
            
            Task: Trim the "age" column from the left by 6 characters
            Example Input: {{"number_of_characters": 6, "location": "left", "columns": "age", "extra_info": null}}
            
            Task: Right trim the "identity" column by 3 characters
            Example Input: {{"number_of_characters": 3, "location": "right", "columns": "identity", "extra_info": null}}
            
            Task: Left trim the "name" column by 2 characters
            Example Input: {{"number_of_characters": 2, "location": "left", "columns": "name", "extra_info": null}}
            
            Task: Trim the "description" column from the right by 5 characters
            Example Input: {{"number_of_characters": 5, "location": "right", "columns": "description", "extra_info": null}}
            
            Task: Right trim the "code" column by 4 characters
            Example Input: {{"number_of_characters": 4, "location": "right", "columns": "code", "extra_info": null}}
            
            Task: Left trim the "address" column by 3 characters
            Example Input: {{"number_of_characters": 3, "location": "left", "columns": "address", "extra_info": null}}

            Task: trim the firstname by 3 and lastname by 5 chracaters from left
            Example Input: [{{"number_of_characters": 3, "location": "left", "columns": "firstname", "extra_info": null}}, {{"number_of_characters": 5, "location": "left", "columns": "lastname", "extra_info": null}}]
            
            Task: Left trim the "test" column by 3 characters
            Example Input: {{"number_of_characters": 3, "location": "left", "columns": "test", "extra_info": "Column does not exist"}}

            You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
            Generate only json parameter and nothing else. Make sure it always has "columns" key.
            """
        return TRIM_COLUMN_PROMPT
    except Exception as e:
        return ""
