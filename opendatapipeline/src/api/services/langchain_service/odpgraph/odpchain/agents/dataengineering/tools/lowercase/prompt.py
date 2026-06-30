from ..dataframe_supplier.df_suppy import get_columns
 
def get_prompt(chat_id, session):
    try:
        #columns_data = get_columns(chat_id, session)
        LOWERCASE_COLUMN_PROMPT = """
            convert all characters within a single or multiple string column(s) to lowercase. The input to this tool is in json format.
            ```json{{
                "columns":[<input to the tool>]
            }}```
           """
        return LOWERCASE_COLUMN_PROMPT
    except Exception as e:
        return ""
