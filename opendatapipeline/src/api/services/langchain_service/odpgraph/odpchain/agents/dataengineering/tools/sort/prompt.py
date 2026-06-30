from ..dataframe_supplier.df_suppy import get_head
 
def get_prompt(chat_id, session):
    try:
        head_data = get_head(chat_id, session)
        SORT_COLUMN_PROMPT = """ 
            sorts the specified columns based on ascending boolean value. The input to this tool is in json format. 
            ```json{{
                "columns":<input to the tool>
                "ascending":<input to the tool>
            }}```
           """
        return SORT_COLUMN_PROMPT
    except Exception as e:
        return ""
