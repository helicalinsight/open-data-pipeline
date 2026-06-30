
from ..dataframe_supplier.df_suppy import get_head, get_metadata


def get_prompt(chat_id, session):
    try:
        metadata_data = get_metadata(chat_id, session)
        AGGREGATIONS_TOOL_PROMPT = f"Consider this metadata: {metadata_data}" + """

        This tool enables users to perform aggregation operations on columns in a dataframe.
        It allows for aggregating data based on specified grouping criteria and applying aggregation functions.
        
        The JSON parameters required for this tool are as follows: {{

                - columns#list#Columns from which to get data to be aggregated.
                - destination_columns#list#Name of the new column(s) in which we want to store the aggregated data.
                - agg#list#Aggregation functions to apply to the data.
                - group_by#list#Field(s) by which we want our data to be grouped.
                - extra_info#string#The extra information like aggregations can perform count for all datatypes and can perform rest of the aggregation functions for non-numeric datatypes.
        }}
        
        Below are a few task descriptions along with their respective input examples:
        
        Task: Perform sum of value1, value2 group by category and subcategory and store it in sum_values.
        Example Input: {{
            "columns": ["value1", "value2"],
            "destination_columns": ["sum_values"],
            "agg": ["sum"],
            "group_by": ["category", "subcategory"],
            "extra_info": null
        }}
        
        Task: Calculate mean of value1, value2 group by category and subcategory and store it in values_mean.
        Example Input: {{
            "columns": ["value1", "value2"],
            "destination_columns": ["values_mean"],
            "agg": ["mean"],
            "group_by": ["category", "subcategory"],
            "extra_info": null
        }}
        
        Task: Calculate mean of value1, value2 
        Example Input: {{
            "columns": ["value1", "value2"],
            "destination_columns": null,
            "agg": ["mean"],
            "group_by": null,
            "extra_info": null
        }}

        Task: Calculate the average time taken to ship the order (difference between `order_date` and `ship_date`).
        Example Input: {{
            "columns": ["order_date", "ship_date"],
            "destination_columns": null,
            "agg": ["mean"],
            "group_by": null,
            "extra_info": "to calculate the average time, we need to subtract order_date - shipdate"
        }}

        Task: Calculate the sum of order_date.
        Example Input: {{
            "columns": ["order_date"],
            "destination_columns": null,
            "agg": ["sum"],
            "group_by": null,
            "extra_info": "the sum of date column cannot be performed"
        }}
        
        Note: The tool will perform the specified aggregation operation(s) on the source columns, grouped by the specified group by columns. If new columns are not provided, the aggregated result will replace the source columns.

        Generate only json parameter and nothing else.
    """
        return AGGREGATIONS_TOOL_PROMPT
    except Exception as e:
        return ""
