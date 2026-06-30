import unittest
import pytest
import json
from src.core.llm import get_chat_model
from unittest.mock import patch
import yaml
import re
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.uppercase.prompt import get_prompt

llm = get_chat_model()
chat_id = "123"
session = "123"

@patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.uppercase.prompt.get_columns')
def SampleAgent(user_input, mock_get_columns):
    mock_get_columns.return_value = ["fullname", "address", "firstname" , "lastname", "name", "email", "department"]
    complete_query =  get_prompt(chat_id, session) + user_input
    response = llm.invoke(complete_query)
    return response.content

user_input = """
- input: Convert "address" and "fullname" columns to uppercase
  expected_output: {"columns": ["address", "fullname"], "extra_info": null}

- input: Convert "fullname", "address", "firstname" and "lastname" columns to uppercase
  expected_output: {"columns": ["fullname", "address", "firstname" , "lastname"], "extra_info": null}

- input: Convert "name" column to upper
  expected_output: {"columns": ["name"], "extra_info": null}

- input: Convert "email" column to upper case
  expected_output: {"columns": ["email"], "extra_info": null}

- input: Convert "department" column to upper
  expected_output: {"columns": ["department"], "extra_info": null}

- input: Convert 1 to upper
  expected_output: {"columns": [1], "extra_info": "Numeric data cannot be converted to upper case."}

  
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

    @pytest.mark.skip()
    def test_responses(self):
        data = yaml.safe_load(user_input)
        count = 0
        for each_item in data:
            count += 1
            with self.subTest(input=each_item["input"]):
                result = SampleAgent(each_item["input"])
                json_output = self.extract_json(result)
                # Checks if the output produced is of type json (dict)
                self.assertTrue(isinstance(json_output, dict))
                # Checks if columns and extra_info are present
                self.assertTrue("columns" in json_output and "extra_info" in json_output, "One or both keys are missing")
                # Checks if the columns is of type list
                self.assertTrue(isinstance(json_output["columns"], list))
                # Checks if the extra_info is of type string or null
                self.assertTrue(isinstance(json_output["extra_info"], str) or json_output["extra_info"] is None)
                if json_output["extra_info"] is not None:
                    # Checks if the extra_info generated is of type string
                    self.assertTrue(isinstance(json_output["extra_info"], str))
                    # Checks if the extra_info generated length is greater than 0
                    self.assertGreater(len(json_output["extra_info"]), 0)
                # Checks if the actual output matches the expected output
                self.assertTrue(
                    self.dicts_are_equal(json_output, each_item['expected_output']),
                    msg=f"Test failed for input: {each_item['input']}. Expected one of {each_item['expected_output']}, but got {json_output}"
                )

# To run the test
if __name__ == '__main__':
    unittest.main()
