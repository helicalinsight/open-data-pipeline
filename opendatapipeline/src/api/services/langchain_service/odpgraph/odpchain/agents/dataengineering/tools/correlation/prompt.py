
from ..dataframe_supplier.df_suppy import get_head
 
def get_prompt(chat_id, session):
    try:
        head_data = get_head(chat_id, session)
        CORRELATION_TOOL_PROMPT = f"Consider this sample data: {head_data}" + """

            This tool facilitates the calculation of correlation values between columns in a dataframe.
            Correlation measures the strength and direction of the linear relationship between two variables.
            
            The JSON parameters required for this tool are as follows:
            
            - columns#List[str]#List of column names to calculate correlation values.
            - destination_column#Optional[str]#Name of the new column to store the result (optional). 
            - extra_info#string#The extra information contains the information which cannot be achieved using correlation like cannot be performed on non-numeric datatypes.
            
            Below are a few task descriptions along with their respective input examples:
            
            Task: Calculate the correlation for age and marks and store it in age_marks_correlation.
            Example Input: {{"columns": ["age", "marks"], "destination_column": "age_marks_correlation", "extra_info": null}}
            
            Task: Calculate the correlation for subject1_marks and subject2_marks.
            Example Input: {{"columns": ["subject1_marks", "subject2_marks"], "destination_column": null, "extra_info": null}}
            
            Note: The tool will compute correlation values between the specified columns. If a destination_column is provided, the result will be stored in that column.

            Generate only json parameter and nothing else. Make sure it always has "columns" key.
        """
        return CORRELATION_TOOL_PROMPT
    except Exception as e:
        return ""
        
