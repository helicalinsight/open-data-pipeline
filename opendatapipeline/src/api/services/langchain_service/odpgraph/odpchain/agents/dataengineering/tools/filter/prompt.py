
from ..dataframe_supplier.df_suppy import get_metadata
 
def get_prompt(chat_id, session):
    try:
        FILTER_COLUMN_PROMPT = """Filters the data based on the specified conditions. The valid list for expr: ['equals', 'not_equals', 'is_greater_than', 'is_lesser_than', 'is_greater_than_or_equal_to', 'is_lesser_than_or_equal_to', 'is_one_of_the', 'is_not_one_of_the', 'in_between', 'not_in_between', 'contains', 'not_contains', 'startswith', 'not_startswith', 'endswith', 'not_endswith', 'is_null', 'is_not_null','is_true','is_false']. The input to this tool is in json format.
            ```json{{
                "columns":<input to the tool>
                "expr":<input to the tool>
                "value":<input to the tool>
            }}```
           """
        return FILTER_COLUMN_PROMPT
    except Exception as e:
        return ""
