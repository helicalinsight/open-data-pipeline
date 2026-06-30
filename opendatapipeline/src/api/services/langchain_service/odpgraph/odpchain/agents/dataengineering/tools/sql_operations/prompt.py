SQL_OPERATIONS_PROMPT = """
    This tool enables users to execute raw SQL queries which are given on natural language on data, providing flexibility in data manipulation.
    The operation involves applying converting natural language queries into sql.
    
    The JSON parameters for this tool are as follows: {{

        - query#str#Query or expression that we want to apply on the data to filter it out.
        - extra_info#string#The extra information like

    }}
    
    Below are a few task descriptions along with their respective input examples:
    
    Task: Execute query "SELECT count(students) FROM df".
    Example Input: {{"query": "SELECT count(students) FROM df", "extra_info": null}}
    
    Task: Run the query "SELECT count(*) FROM df WHERE age > 25".
    Example Input: {{"query": "SELECT count(*) FROM df WHERE age > 25", "extra_info": null}}
    
    You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
    Generate only json parameter and nothing else. Make sure it always has "query" key.
"""
