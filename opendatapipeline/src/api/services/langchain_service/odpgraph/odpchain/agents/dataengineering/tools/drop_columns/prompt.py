
from ..dataframe_supplier.df_suppy import get_columns
 
def get_prompt(chat_id, session):
    try:
        DROP_COLUMNS_PROMPT = """
            drops single or multiple column(s) from the dataset. The input to this tool is in json format. 
            ```json{{
                "columns":[<input to the tool>]
            }}```
           """
        return DROP_COLUMNS_PROMPT
    except Exception as e:
        return ""
