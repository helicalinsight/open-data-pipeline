import unittest
import json
from src.core.llm import get_chat_model
import yaml
from src.api.services.langchain_service.odpgraph.llm_prompts.intent_prompt import intent_prompt

llm = get_chat_model()


def SampleAgent(user_input):
    complete_query =  intent_prompt + user_input
    response = llm.invoke(complete_query)
    return json.loads(response.content)

demo_prompts = """
- input: union 2017_Order_Data, 2019_Order_Data, 2020_Order_Data
  expected_output: union

- input: cast order_id as string data type
  expected_output: cast

- input: remove all the records which are starting with XXX from order_id column
  expected_output: filter

- input: split customer_id using - into client_id and client_name
  expected_output: split

- input: add a new column called as profit which is revenue - cost 
  expected_output: arithmetic_operations, pytool
  
- input: add a new column called delay in days = ship_date - order_date
  expected_output: arithmetic_operations, pytool
  
- input: duplicate profit column to profit_margin 
  expected_output: pytool
  
- input: when cost is between 0 to 1000 then low, when cost is between 1001 to 2000 then medium, else high
  expected_output: when_otherwise
  
- input: extract day from order_date and save that in a new column called Day_Name
  expected_output: pytool, analysis
"""

tool_prompts = """
- input: Create a new column called as net_revenue by subtracting 100 from revenue column 
  expected_output: arithmetic_operations
  
- input: Add column test with default value as 10
  expected_output: add_columns

- input: find sum of age column
  expected_output: aggregations
  
- input: Concatenate customer id column with customer name using – as delimiter
  expected_output: concat

- input: Find correlation between public_id and age column
  expected_output: correlation
  
- input: change working file to enrollments
  expected_output: CurrentWorkingFile

- input: Drop customer_id column
  expected_output: drop_columns
  
- input: Drop all columns except customer_id column
  expected_output: drop_all_except_columns
  
- input: Change the order_date column format to yyyy/mm/dd
  expected_output: date_format
  
- input: Deduplicate lastname column
  expected_output: deduplicate

- input: Drop null values from zipcode column 
  expected_output: drop_null

- input: Export data to abc.csv 
  expected_output: export

- input: Extract year from order_date column 
  expected_output: extract

- input: Fill all null values with 00 
  expected_output: fill_na

- input: filter records where age column values > 10 
  expected_output: filter

- input: join orders, customers using customer_id 
  expected_output: joins

- input: Change the customer_id column to lower case 
  expected_output: lowercase

- input: Rename customer_id to cid 
  expected_output: rename

- input: Replace – with , in customer_id column 
  expected_output: replace

- input: Sort customer_id column in ascending order 
  expected_output: sort

- input: Split customer_id to id, name using - delimiter 
  expected_output: split

- input: calculate profit 
  expected_output: analysis, pytool

- input: Trim the age column from the left by 6 characters
  expected_output: trim

- input: Union file1 and file2 
  expected_output: union

- input: Change the customer_id column to upper case 
  expected_output: uppercase

- input: If the age is greater than 20, classify it as 'Adult'; if the age is between 15 and 19, classify it as 'Young'; otherwise, classify it as 'Child'. 
  expected_output: when_otherwise, analysis

- input: Cast firstname column to fname 
  expected_output: cast
"""

extra_prompts = """
- input: join 2020_Order_Data and 2019_Order_Data on order_id
  expected_output: joins

- input: join students and teachers on teacher_id
  expected_output: joins

- input: join enrollments and orders on eid
  expected_output: joins

- input: join test, test1, test2 using common column
  expected_output: joins

- input: join wegeh45w543ew, eroihotheoivh using ergt
  expected_output: joins

- input: join public_equipmentgenerelinfo, public_workordermaster using worm_eqpm_id, eqpgi_eqpm_id
  expected_output: joins
  
- input: Find correlation between public_id and age column
  expected_output: correlation

- input: calculate correlation between revenue and cost column
  expected_output: correlation
  
- input: Find correlation between public_id and age column
  expected_output: correlation

- input: calculate correlation between cookies_shipped and cost column
  expected_output: correlation
  
- input: when age is greater than 20, then mark as mature, else child
  expected_output: when_otherwise

- input: when age is greater than 20, classify as mature, else child
  expected_output: when_otherwise
  
- input: if age is greater than 20, then mark as mature, else child
  expected_output: when_otherwise

- input: if age is greater than 20, classify as mature, else child
  expected_output: when_otherwise
  
- input: If the age is greater than 20, classify it as 'Adult'; if the age is between 15 and 19, classify it as 'Young'; otherwise, classify it as 'Child'.
  expected_output: when_otherwise

- input: Create a bin for age column and assign them a lable accordingly
  expected_output: when_otherwise, pytool

- input: sort order_id column
  expected_output: sort

- input: sort customer_id column
  expected_output: sort

- input: Sort customer_id column in ascending order
  expected_output: sort

- input: Sort order_id and Costumerie together in ascending order.
  expected_output: sort

- input: Sort order_id in ascending order and customer_id in descending order.
  expected_output: sort
"""
class TestResponses(unittest.TestCase):
    
    @unittest.skip("Temporarily skipping this test case")
    def test_responses(self):
        # Sample data (this would be your user_input parsed via yaml.safe_load())
        user_input = demo_prompts + tool_prompts + extra_prompts
        data = yaml.safe_load(user_input)
        count = 0
        for each_item in data:
            count += 1
            #print(each_item)
            with self.subTest(input=each_item["input"]):
                result = SampleAgent(each_item["input"])
                #print("result", result)
                #print("Count:", count, "Result:", result["intent"], "Expected:", each_item['expected_output'])
                self.assertIn(result["intent"], each_item['expected_output'], 
                          msg=f"Test failed for input: {each_item['input']}. Expected one of {each_item['expected_output']}, but got {result['intent']}")

# To run the test
if __name__ == '__main__':
    unittest.main()
