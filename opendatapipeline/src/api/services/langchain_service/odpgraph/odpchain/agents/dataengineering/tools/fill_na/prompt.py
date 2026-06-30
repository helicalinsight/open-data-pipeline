
from ..dataframe_supplier.df_suppy import get_head
 
def get_prompt(chat_id, session):
    try:
        FILL_NA_PROMPT = f"Consider this sample data: {get_head(chat_id, session)}" + """
        
            This tool facilitates the filling of null values (NaNs) in a dataframe.
            It allows for specifying the column, value, method, axis, limit and extra_info for the fillna operation.
            
            The column, value, method, axis, limit and extra_info parameters are optional. If no column value is provided, it will default to "". If no value is provided, it will default to None. If no method value is provided, it will default to None. If no axis value is provided, it will default to 0. If no limit value is provided, it will default to None. If no extra_info value is provided, it will default to None.
            
            The JSON parameters required for this tool are as follows: {{

                - column#Optional[str]#The name of the column where fillna operation will be performed.
                - value#Optional[Union[str, int, float, bool]]#The value used to fill NaNs.
                - method#Optional[str]#The method used to fill NaNs ('ffill', 'bfill', etc.).
                - axis#Optional[Union[str, int]]#The axis along which to fill NaNs ('index' or 'columns').
                - limit#Optional[int]#The maximum number of consecutive NaNs to forward/backward fill.
                - extra_info#string#The extra information like
            
            }}
            
            Below are several task descriptions along with their respective input examples.
            
            Task: Fill null values with value 0.
            Example Input: {{"column": null, "value": 0, "method": null, "axis": null, "limit": null, "extra_info": null}}
            
            Task: Fill all nulls of column helical with value 0 and column helicalB with value 10.
            Example Input: {{"column": null, "value": {{'helical': 0, 'helicalB': 10}}, "method": null, "axis": null, "limit": null, "extra_info": null}}
            
            Task: Update the null values in the column testing_column with 55
            Example Input: {{"column": "testing_column", "value": 55, "method": null, "axis": null, "limit": null, "extra_info": null}}
            
            Task: Fill all the nulls using bfill method.
            Example Input: {{"column": null, "value": null, "method": "bfill", "axis": null, "limit": null, "extra_info": null}}
            
            Task: Fill all the nulls using ffill method.
            Example Input: {{"column": null, "value": null, "method": "ffill", "axis": null, "limit": null, "extra_info": null}}
            
            Task: Fill null values of column city with value as "No City".
            Example Input: {{"column": "city", "value": "No City", "method": null, "axis": null, "limit": null, "extra_info": null}}
            
            Task: Fill the first null value of column city using ffill method.
            Example Input: {{"column": "city", "value": null, "method": "ffill", "axis": null, "limit": 1, "extra_info": null}}
            
            Task: Fill the "Full" value along columns axis.
            Example Input: {{"column": null, "value": "Full", "method": null, "axis": "columns", "limit": null, "extra_info": null}}
            
            Task: Fill the "Empty" value along index axis.
            Example Input: {{"column": null, "value": "Empty", "method": null, "axis": 0, "limit": null, "extra_info": null}}

            You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
            Generate only json parameter and nothing else.
        """
        return FILL_NA_PROMPT
    except Exception as e:
        return ""
