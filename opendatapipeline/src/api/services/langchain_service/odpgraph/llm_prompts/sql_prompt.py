# sql_prompt="""Your task is to Generate the sql query for the given input. 
#         You will be provided with a natural language input query. 
#         Your agent should take a user query as input and genereate the sql query in the presto dailect for the given quyery. 
        
#         the table name will always be df. 
#         For example, 

#         Task: "Show all employees whose salary is above $100,000."
#         Expected Output: sql```select * from df where salary > 100000```
        
#         Task: "List all products with a price higher than $50."
#         Expected Output: sql```select * from df where price > 50```
        
#         Task: "Display all orders placed after January 1st, 2023."
#         Expected Output: sql```select * from df where order_date > '2023-01-01'```
        
#         Task: "Find all customers who live in New York City."
#         Expected Output: sql```select * from df where city = 'New York City'```
        
#         Task: "Show all employees in the IT department."
#         Expected Output: sql```select * from df where department = 'IT'```
        
#         Task: "show me top 10 inventory_id where last_update date is last month"
#         Expected Output: sql```SELECT inventory_id FROM df WHERE date_format(last_update, 'yyyy-MM') = date_format(add_months(current_date, -1), 'yyyy-MM') ORDER BY last_update DESC LIMIT 10;```
        
#         Your output should only include the sql query inside ``` ```.. 
#         Following is the query: """


