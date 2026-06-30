CURRENT_WORKING_FILE_PROMPT = """
    This tool is designed to choose the current working file. 
    It takes one parameter: file, which is the name of the current working file. 
    The input to this tool will be used to set the specified file as the current working file.

    The file parameter is required.

    The JSON parameter for this tool is as follows: {{

        - file#string#The name of the current working file.

    }}

    Below are several task descriptions along with their respective input examples.
    
    Task: Choose "student" file as the current working file
    Example Input: {{"file": "student"}}
    
    Task: Select "grades" as the current file
    Example Input: {{"file": "grades"}}
    
    Task: Set sales_data as the current working file
    Example Input: {{"file": "sales_data"}}
    
    Task: Make "inventory" the current file
    Example Input: {{"file": "inventory"}}
    
    Task: Choose expenses file as the current working file
    Example Input: {{"file": "expenses"}}

    You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
    Generate only json parameter and nothing else. Make sure it always has "file" key.
    """
