from ..dataframe_supplier.df_suppy import get_head
 
def get_prompt(chat_id, session):
    try:
        head_data = get_head(chat_id, session)
        REPLACE_SPECIAL_CHARACTERS_PROMPT = f"Consider this sample data: {head_data}" + """

            This tool is designed to replace a specified special character in a column with a new character. It takes four parameters: source_column, target_character, replacement_character and extra_info.
            The input to this tool will be used to replace the specified target special character with the replacement character in the given source column.

            The columns, target_character and replacement_character parameters are required, while the extra_info parameter is optional. If no extra_info value is provided, it will default to None.

            The JSON parameters for this tool are as follows: {{

                - columns#string#The name of the column containing text with special characters.
                - target_character#string#The special character to be replaced in the source column.
                - replacement_character#string#The character that will replace the target special character.
                - extra_info#string#The extra information like when the column specified does not exist.

            }}
            
            Below are several task descriptions along with their respective input examples.
            
            Task: Replace '-' from "age" column with '_'
            Example Input: {{"columns": "age", "target_character": "-", "replacement_character": "_", "extra_info": null}}
            
            Task: Replace all occurrences of '$' with space from "dateidentity" column
            Example Input: {{"columns": "dateidentity", "target_character": "$", "replacement_character": " ", "extra_info": null}}
            
            Task: Replace '&' from "description" column with '#'
            Example Input: {{"columns": "description", "target_character": "&", "replacement_character": "#", "extra_info": null}}
            
            Task: Replace '#' from "phone_number" column with '-'
            Example Input: {{"columns": "phone_number", "target_character": "#", "replacement_character": "-", "extra_info": null}}
            
            Task: Replace '*' from "email" column with '@'
            Example Input: {{"columns": "email", "target_character": "*", "replacement_character": "@", "extra_info": null}}
            
            Task: Replace '%' from "address" column with '+'
            Example Input: {{"columns": "address", "target_character": "%", "replacement_character": "+", "extra_info": null}}
            
            Task: Replace '%' from address
            Example Input: {{"columns": "address", "target_character": "%", "replacement_character": "", "extra_info": null}}
            
            Task: Replace '%' from test
            Example Input: {{"columns": "test", "target_character": "%", "replacement_character": "", "extra_info": "Column does not exist"}}

            You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
            Generate only json parameter and nothing else. Make sure it always has "columns", "target_character", "replacement_character" keys.
            """
        return REPLACE_SPECIAL_CHARACTERS_PROMPT
    except Exception as e:

        return ""
