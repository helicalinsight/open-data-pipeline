def get_prompt(chat_id, session):
    try:
        EXPORT_PROMPT = """
            This tool allows users to export data to a CSV file.
            The tool requires the desired export file name, which is optional.
            
            The input parameters required for this tool are as follows:
            
            - export_name#string#The name of the CSV file that the user wants to export to.
            
            Below are a few task descriptions along with their respective input examples:
            
            Task: Export data to file "file1.csv".
            Example Input: {{"export_name": "file1.csv"}}
            
            Task: Execute export of data to the file "file1.csv".
            Example Input: {{"export_name": "file1.csv"}}
            
            Task: Export information to the file "file1.csv".
            Example Input: {{"export_name": "file1.csv"}}
            
            Task: Export data.
            Example Input: {{"export_name": null}}
            
            Note: The tool will export the specified data from the source file to a CSV file with the provided name. If export_name is not provided, it defaults to the value of source_file suffixed by .csv.
            """
        return EXPORT_PROMPT
    except Exception as e:
        return ""
