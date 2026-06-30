import unittest
import json
from src.core.llm import get_chat_model
from unittest.mock import patch
import yaml
import re
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.aggregations.prompt import get_prompt

llm = get_chat_model()
chat_id = "123"
session = "123"

@patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.aggregations.prompt.get_metadata')
def SampleAgent(user_input, mock_get_metadata):
    mock_get_metadata.return_value = """CREATE TABLE employee_data (
    id INTEGER,
    name TEXT,
    age INTEGER,
    salary FLOAT,
    is_active BOOLEAN,
    join_date TIMESTAMP
);
"""
    complete_query =  get_prompt(chat_id, session) + user_input
    response = llm.invoke(complete_query)
    return response.content

user_input = """
- input: Perform sum of value1, value2 group by category and subcategory and store it in sum_values.
  expected_output: {
            "columns": ["value1", "value2"],
            "destination_columns": ["sum_values"],
            "agg": ["sum"],
            "group_by": ["category", "subcategory"],
            "extra_info": null
        }

- input: Calculate mean of value1, value2 group by category and subcategory and store it in values_mean.
  expected_output: {
            "columns": ["value1", "value2"],
            "destination_columns": ["values_mean"],
            "agg": ["mean"],
            "group_by": ["category", "subcategory"],
            "extra_info": null
        }

- input: Calculate mean of value1, value2 
  expected_output: {
            "columns": ["value1", "value2"],
            "destination_columns": null,
            "agg": ["mean"],
            "group_by": null,
            "extra_info": null
        }
            
- input: Calculate the average time taken to ship the order (difference between `order_date` and `ship_date`).
  expected_output: {
            "columns": ["order_date", "ship_date"],
            "destination_columns": null,
            "agg": ["mean"],
            "group_by": null,
            "extra_info": "to calculate the average time, we need to subtract order_date - shipdate"
        }
"""

class TestResponses(unittest.TestCase):
    def dicts_are_equal(self, dict1, dict2):
        """
        Helper function to compare two dictionaries, allowing for key order differences.
        """
        return json.dumps(dict1, sort_keys=True) == json.dumps(dict2, sort_keys=True)

    def extract_json(self, string):
        """
        Helper function to extract json from string.
        """
        json_pattern = r'({.*?})'  # Capture the JSON object.
        # Attempt to match a JSON object (inline or markdown)
        json_match = re.search(json_pattern, string, re.DOTALL)
        if json_match:
            # Extract the JSON string
            json_string = json_match.group(1).strip()
            try:
                # Parse the JSON string into a Python dictionary
                json_data = json.loads(json_string)
                return json_data
            except json.JSONDecodeError:
                # Return None if parsing fails
                return None
        # Return None if no valid JSON was found
        return None
    
    @unittest.skip("Temporarily skipping this test case")
    def test_responses(self):
        data = yaml.safe_load(user_input)
        count = 0
        for each_item in data:
            count += 1
            with self.subTest(input=each_item["input"]):
                result = SampleAgent(each_item["input"])
                json_output = self.extract_json(result)
                self.assertTrue(
                    self.dicts_are_equal(json_output, each_item['expected_output']),
                    msg=f"Test failed for input: {each_item['input']}. Expected one of {each_item['expected_output']}, but got {json_output}"
                )

# To run the test
if __name__ == '__main__':
    unittest.main()
