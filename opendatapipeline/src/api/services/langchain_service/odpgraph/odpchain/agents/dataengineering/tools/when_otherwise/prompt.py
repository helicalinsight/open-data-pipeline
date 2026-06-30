from ..dataframe_supplier.df_suppy import get_head
 
def get_prompt(chat_id, session):
    try:
        WHEN_OTHERWISE_PROMPT = """ 
            Construct SELECT query on df to handle CASE expression along with all the columns. Default the new column to "__newcolumn__". The input to this tool is in json format. 
            ```json{{
                "query":<input to the tool>
            }}```
           """
        return WHEN_OTHERWISE_PROMPT
    except Exception as e: 
        return ""
