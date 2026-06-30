import unittest
import json
from src.core.llm import get_chat_model
from unittest.mock import patch
import yaml
import re
import pytest
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.correlation.prompt import get_prompt

llm = get_chat_model()
chat_id = "123"
session = "123"

@patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.correlation.prompt.get_head')
def SampleAgent(user_input, mock_get_head):
    mock_get_head.return_value = """|    | ID   | Name    |   Age | City        |
|---:|------|---------|------:|-------------|
|  0 | 1    | Alice   |    25 | New York    |
|  1 | 2    | Bob     |    30 | Los Angeles |
|  2 | 3    | Charlie |    35 | Chicago     |
"""
    complete_query =  get_prompt(chat_id, session) + user_input
    response = llm.invoke(complete_query)
    return response.content

user_input = """
- input: Calculate the correlation for age and marks and store it in age_marks_correlation.
  expected_output: {"columns": ["age", "marks"], "destination_column": "age_marks_correlation", "extra_info": null}

- input: Calculate the correlation for subject1_marks and subject2_marks.
  expected_output: {"columns": ["subject1_marks", "subject2_marks"], "extra_info": null}
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
                self.assertTrue(
                    self.dicts_are_equal(json_output, each_item['expected_output']),
                    msg=f"Test failed for input: {each_item['input']}. Expected one of {each_item['expected_output']}, but got {json_output}"
                )

# To run the test
if __name__ == '__main__':
    unittest.main()
