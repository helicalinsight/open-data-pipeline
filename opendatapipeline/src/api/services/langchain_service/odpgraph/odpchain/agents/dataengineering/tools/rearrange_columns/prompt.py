
from ..dataframe_supplier.df_suppy import get_head
 
def get_prompt(chat_id, session):
    try:
        REARRANGE_COLUMNS_PROMPT = """
        Useful for when you need to rearrange the columns of any dataframe or table.
        Use the columns list provided below to know the actual position of the columns.
        
        The input to this tool is in json format. 
        {{"columns":[{{
            "column": <input the column name>,
            "position": <input the column index position>
        }}]
        }}

        Explanation of input:
        1. The "column" field indicates the name of the column you want to move.
        2. The "position" field indicates the index position where you want to place the column.
            - Positive numbers represent the index starting from the first column (0-based index).
            - Negative numbers represent positions counting from the end of the table. For example:
                a. -1 is the last position,
                b. -2 is the second last position and so on.
        Here are some examples of rearranging columns:
        example_user: move col1 next to col5 column
        example_input: {{"columns":[{{"col5":0}},{{"col1":1}}]}}

        example_user: Move col2 before col1 column
        example_input: {{"columns":[{{"col2":0}},{{"col1":1}}]}}

        example_user: move email to first position
        example_input : {{"columns":[{{"email":0}}]}}

        example_user: move customer to last position
        example_input: {{"columns":[{{"customer":-1}}]}}

        example_user: move marks to second last position
        example_input: {{"columns":[{{email":-2}}]}}
        """
        return REARRANGE_COLUMNS_PROMPT
    except Exception as e:
        return ""
