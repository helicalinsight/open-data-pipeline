import unittest
from src.core.llm import get_chat_model
import yaml
from src.api.services.pyspark_service.utils import Utils
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.pytool.prompt import get_pytool_prompt
from unittest.mock import MagicMock, patch

llm = get_chat_model()
chat_id = "123"
session = "123"
cwf_name="Data_2017"
utils = Utils()

@patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.pytool.prompt.CreateDFDictionary.create')
@patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.pytool.prompt.get_dataframe_schema')
@patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.pytool.prompt.get_head')
def SampleAgent(user_input, mock_get_head, mock_get_dataframe_schema, mock_create_instance):
    mock_session = MagicMock()
    mock_create_instance.return_value = {"mock_key": "mock_value"}
    mock_get_dataframe_schema.return_value = "mock string"
    mock_get_head.return_value = """|    | ID   | Name    |   Age | City        |
|---:|------|---------|------:|-------------|
|  0 | 1    | Alice   |    25 | New York    |
|  1 | 2    | Bob     |    30 | Los Angeles |
|  2 | 3    | Charlie |    35 | Chicago     |
"""
    complete_query =  get_pytool_prompt(chat_id, mock_session, cwf_name) + user_input
    response = llm.invoke(complete_query)
    return response.content


class TestResponses(unittest.TestCase):
    
    @unittest.skip("Temporarily skipping this test case")
    def test_using_llm(self):
        if not hasattr(self, 'output'):
            self.output = ""
        if not hasattr(self, 'user_input'):
            self.user_input = ""
        complete_query = f"""
    You are given a specific piece of code. Your task is to verify whether the provided code correctly matches the user's input.
    1. Review the code: Read and understand the code that has been shared.
    2. Analyze the user input: Carefully examine the user's input.
    3. Verify the match: Check if the code correctly applies to the user's input.
    4. Return only "True" if the code matches the user's input, or "False" if it does not match. 
    Here's the code: {self.output}
    Here's the user's input: {self.user_input}
    """
        response = llm.invoke(complete_query)
        return response.content
    
    @unittest.skip("Temporarily skipping this test case")
    def test_responses(self):
        user_input = """
        - Rearrange the columns, place ""lastname"" right before ""firstname"".
        - Create current_timestamp column with current time
        - Cast address column to json
        - add a column todays_date with default value as todays date
        """
        data = yaml.safe_load(user_input)
        count = 0
        for each_item in data:
            count += 1
            with self.subTest(input=each_item):
                result = SampleAgent(each_item)
                self.user_input = each_item
                self.output = utils.extract_code(result)
                test_output = self.test_using_llm()
                self.assertTrue(test_output)

# To run the test
if __name__ == '__main__':
    unittest.main()
