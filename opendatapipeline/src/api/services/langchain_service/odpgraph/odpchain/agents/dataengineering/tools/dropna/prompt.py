
from ..dataframe_supplier.df_suppy import get_head
 
def get_prompt(chat_id, session):
    try:
        DROPNA_PROMPT = f"Consider this sample data: {get_head(chat_id, session)}" + """
        
            This tool is designed to remove rows with missing values (NaN/null) from a dataset. It takes two parameters: subset and extra_info. 
            If specified, only the rows with missing values in those columns will be removed.
            If subset is not provided, rows with any missing values in any column will be removed.

            The subset and extra_info parameters are optional.
            If subset is not provided, all columns will be considered for removing rows with missing values.

            The JSON parameter for this tool is as follows: {{

                - subset#list#The list of column names. If specified, only rows with missing values in these columns will be removed.
                - extra_info#string#The extra information contains information like 

            }}
            
            Below are several task descriptions along with their respective input examples.

            Task: Remove rows with missing values in the "age" column
            Example Input: {{"subset": ["age"], "extra_info": null}}
            
            Task: Remove rows with missing values in the "weight" and "height" columns
            Example Input: {{"subset": ["weight", "height"], "extra_info": null}}
            
            Task: Remove rows with missing values in the "name" column
            Example Input: {{"subset": ["name"], "extra_info": null}}
            
            Task: Remove rows with missing values in the "code" column
            Example Input: {{"subset": ["code"], "extra_info": null}}
            
            Task: Remove rows with missing values in the "department" column
            Example Input: {{"subset": ["department"], "extra_info": null}}
            
            Task: Remove rows with missing values in the "email" and "phone" columns
            Example Input: {{"subset": ["email", "phone"], "extra_info": null}}

            Task: Do not remove any row
            Example Input: {{"subset": [], "extra_info": null}}

            You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
            Generate only json parameter and nothing else.
            """
        return DROPNA_PROMPT
    except Exception as e:
        return ""
