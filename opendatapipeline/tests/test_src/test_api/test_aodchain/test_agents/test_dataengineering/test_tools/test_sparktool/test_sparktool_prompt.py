import unittest
from src.core.llm import get_chat_model
import yaml
from src.api.services.pyspark_service.utils import Utils
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.sparktool.prompt import get_sparktool_prompt

llm = get_chat_model()
chat_id = "123"
session = "123"
cwf_name="Data_2017"
utils = Utils()

def SampleAgent(user_input):
    complete_query =  get_sparktool_prompt(user_input["pandas_code"])
    response = llm.invoke(complete_query)
    return response.content

user_input = """
- pandas_code: |
    df = DataframeInformation.get(alias="Data_2017")
    df["profit"] = df["revenue"] - df["cost"]
    DataframeInformation.update(alias="Data_2017", dataframe=df)
  user_task: create a new column called profit which is revenue - cost
- pandas_code: |
    import datetime
    df = DataframeInformation.get(alias="Data_2017")
    df['current_timestamp'] = datetime.datetime.now()
    DataframeInformation.update(alias="Data_2017", dataframe=df)
  user_task: Create current_timestamp column with current time
- pandas_code: |
    from fuzzywuzzy import fuzz
    old_prd_dataset = DataframeInformation.get(alias="old_prd_dataset")
    new_prd_dataset = DataframeInformation.get(alias="new_prd_dataset")
    new_prd_dataset['merge']='all'
    old_prd_dataset['merge']='all'
    all_products = pd.merge(new_prd_dataset,old_prd_dataset,on='merge')
    del all_products['merge']
    products_tuple = all_products[['old_product_name', 'new_product_name']].apply(tuple, axis=1).tolist()
    all_products['ratio'] = [fuzz.ratio(*i) for i in products_tuple]
    all_products = all_products[all_products.ratio>70]
  user_task: Compare the old product name with the new product name, and merge them if they match by at least 70%.
    """

class TestResponses(unittest.TestCase):
    @unittest.skip("Temporarily skipping this test case")
    def test_using_llm(self):
        if not hasattr(self, 'output'):
            self.output = ""
        if not hasattr(self, 'task'):
            self.task = ""
        complete_query = f"""
    You are given a specific piece of code. Your task is to verify whether the provided code correctly matches the user's input.
    1. Review the code: Read and understand the code that has been shared.
    2. Analyze the user input: Carefully examine the user's input.
    3. Verify the match: Check if the code correctly applies to the user's input.
    4. Return only "True" if the code matches the user's input, or "False" if it does not match. 
    Here's the code: {self.output}
    Here's the user's input: {self.task}
    """
        response = llm.invoke(complete_query)
        return response.content
    
    @unittest.skip("Temporarily skipping this test case")
    def test_responses(self):
        data = yaml.safe_load(user_input)
        count = 0
        for each_item in data:
            count += 1
            with self.subTest(input=each_item):
                result = SampleAgent(each_item)
                self.output = utils.extract_code(result)
                self.task = each_item["user_task"]
                test_output = self.test_using_llm()
                self.assertTrue(test_output)


# To run the test
if __name__ == '__main__':
    unittest.main()
