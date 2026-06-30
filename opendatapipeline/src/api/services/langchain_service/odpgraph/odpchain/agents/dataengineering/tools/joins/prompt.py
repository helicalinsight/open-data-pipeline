JOIN_FILES_PROMPT = """
    This tool is designed to join files based on specified conditions. 
    It takes five parameters: file_names, left_on, right_on, join_type and extra_info.
    The input to this tool will be used to join the specified files using the specified columns and join type.

    All parameters are required, while the extra_info is optional. If no extra_info value is provided, it will default to None.

    The JSON parameters for this tool are as follows: {{

        - file_names#list#The list of file names to join.
        - left_on#string or list#The column from the left dataset to join on.
        - right_on#string or list#The column from the right dataset to join on.
        - join_type#string#The type of join to perform (e.g., inner, outer, left, right).
        - extra_info#string#The extra information like

    }}

    Below are several task descriptions along with their respective input examples.
    
    Task: Join "Enrollments" and "Students" files using "identity" from Enrollments and "id" from Students by left join
    Example Input: {{"file_names": ["Enrollments", "Students"], "left_on": "identity", "right_on": "id", "join_type": "left", "extra_info": null}}
    
    Task: Join "helical" and "aod" files by "id" and "aod_id" with inner join
    Example Input: {{"file_names": ["helical", "aod"], "left_on": ["id", "dept"], "right_on": ["aod_id", "aod_dept"], "join_type": "inner", "extra_info": null}}
    
    Task: Join "orders" and "customers" files using "order_id" from orders and "customer_id" from customers by outer join
    Example Input: {{"file_names": ["orders", "customers"], "left_on": "order_id", "right_on": "customer_id", "join_type": "outer", "extra_info": null}}
    
    Task: Join "products" and "categories" files by "product_id" and "category_id" with right join
    Example Input: {{"file_names": ["products", "categories"], "left_on": "product_id", "right_on": "category_id", "join_type": "right", "extra_info": null}}
    
    Task: Join "sales" and "regions" files using "sales_rep" from sales and "region_code" from regions by inner join
    Example Input: {{"file_names": ["sales", "regions"], "left_on": "sales_rep", "right_on": "region_code", "join_type": "inner", "extra_info": null}}
    
    You should only perform the task which is given to you. Do not attempt to perform anything by yourself.
    Generate only json parameter and nothing else. Make sure it always has "file_names", "left_on", "right_on" and "join_type" keys.
    """
