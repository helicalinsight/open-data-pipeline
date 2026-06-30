UNION_TOOL_PROMPT = """
    This tool facilitates the union operation on two or more dataframes, merging them into a single new dataframe.
    The operation involves combining rows from two or more dataframes based on common column values.
    It takes three parameters: file_names, columns and extra_info. 
    
    The file_names parameter is required, while columns and extra_info are optional. If no columns value is provided, it will default to None. If no extra_info value is provided, it will default to None.
    
    The JSON parameters for this tool are as follows: {{

        - file_names#list# Files on which we want to perform the union operation.
        - columns#List[str]#Fields on which we want to perform the union operation.
        - extra_info#string#The extra information like 
    
    }}
    
    Below are a few task descriptions along with their respective input examples:
    
    Task: Union "Students_2023" and "Students_2024" files.
    Example Input: {{"columns": null, "file_names":["Students_2023","Students_2024"], "extra_info": null}}
    
    Task: Union "Students" and "StudentsEnrollments" files.
    Example Input: {{"columns": null, "file_names":["Students","StudentsEnrollments"], "extra_info": null}}
    
    Task: Union "products_2023" and "products_2024" files based on column grade.
    Example Input: {{"columns": ["grade"],"file_names":["products_2023","products_2024"], "extra_info": null}}
    
    You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
    Generate only json parameter and nothing else. Make sure it always has "file_names" key.
"""
