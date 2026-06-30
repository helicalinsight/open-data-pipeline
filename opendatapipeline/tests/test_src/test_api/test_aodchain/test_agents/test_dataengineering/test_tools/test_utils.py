import unittest
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.utils import extract_code
import re


class TestUtils(unittest.TestCase):
    def test_extract_code_without_python(self):
        text_without_py = """Libraries: SparkSession is not present in the given code.

Code: <code>
df = DataframeInformation.get(alias="enrollments__1_")
df['age'].fillna(value=0, inplace=True)
DataframeInformation.update(alias="enrollments__1_", dataframe=df)
</code>
"""
        code = extract_code(text_without_py)
        expected_code = """df = DataframeInformation.get(alias="enrollments__1_")
df['age'].fillna(value=0, inplace=True)
DataframeInformation.update(alias="enrollments__1_", dataframe=df)"""
        self.assertEqual(code, expected_code)
    
    def test_extract_code_with_python(self):
        text_with_py = """Here's the converted Spark code for your task:

```python
Libraries: DataframeInformation is already available in spark code. Sparksession and other variables are also present. do not include them.
Code: <code>
df = DataframeInformation.get(alias="enrollments__1_")
df['age'] = df['age'].fillna(0)
DataframeInformation.update(alias="enrollments__1_", dataframe=df)
</code>
```
"""
        code = extract_code(text_with_py)
        expected_code = """df = DataframeInformation.get(alias="enrollments__1_")
df['age'] = df['age'].fillna(0)
DataframeInformation.update(alias="enrollments__1_", dataframe=df)"""
        self.assertEqual(code, expected_code)


if __name__ == "__main__":
    unittest.main()



# import ast
# import astor


# class ExtractMessagesVisitor(ast.NodeVisitor):
#     def __init__(self):
#         self.messages = {}

#     def visit_FunctionDef(self, node):
#         # Process each function in the code
#         self.current_function = node.name
#         self.generic_visit(node)

#     def visit_Assert(self, node):
#         if isinstance(node.test, ast.Compare):
#             left = node.test.left
            
#             if isinstance(left, ast.Call):
#                 if isinstance(left.func, ast.Attribute) and left.func.attr == 'get':
#                     if len(left.args) > 0 and isinstance(left.args[0], ast.Constant):
#                         if isinstance(node.test.comparators[0], ast.Constant):
#                             self.messages[self.current_function] = node.test.comparators[0].value
#         self.generic_visit(node)

# class FunctionTransformer(ast.NodeTransformer):
#     def __init__(self, messages):
#         self.messages = messages

#     def visit_FunctionDef(self, node):
#         if node.name in self.messages:
#             message = self.messages[node.name]
#             print("message:", message)
#             try:
#                 code_1="mock_execute_service_instance = MockExecuteService.return_value"
#                 new_code = f'mock_execute_service_instance.execute.return_value = [{{"text": """{message}"""}}]/n'
#                 node.body.insert(0, ast.parse(new_code).body[0])
#                 node.body.insert(0, ast.parse(code_1).body[0])
#             except:
#                 code_1="mock_execute_service_instance = MockExecuteService.return_value"
#                 new_code = f"mock_execute_service.execute.return_value = [{{'text': '''{message}'''}}]/n"
#                 node.body.insert(0, ast.parse(new_code).body[0])
#                 node.body.insert(0, ast.parse(code_1).body[0])
#         return self.generic_visit(node)

# def modify_code(source_code):
#     # Parse the source code into an AST
#     tree = ast.parse(source_code)
    
#     # Extract messages from the AST
#     visitor = ExtractMessagesVisitor()
#     visitor.visit(tree)
#     messages = visitor.messages
    
#     if not messages:
#         raise ValueError("No messages found in the test cases.")
    
#     # Transform the AST
#     transformer = FunctionTransformer(messages)
#     new_tree = transformer.visit(tree)

#     # Generate the modified source code
#     new_source_code = astor.to_source(new_tree)
#     return new_source_code

# def read_file(file_path):
#     with open(file_path, 'r') as file:
#         return file.read()

# def write_file(file_path, content):
#     with open(file_path, 'w') as file:
#         file.write(content)
        


# def modify_file(file_path):
#     original_code = read_file(file_path)
#     try:
#         modified_code = modify_code(original_code)
#         write_file(file_path, modified_code)
#         print(f"Code modified successfully in {file_path}")
#     except ValueError as e:
#         print(e)

# # Modify the file
# file_path = 'C:/Users/Helical/Desktop/Helical/ml_new/ml/askondata/tests/test_src/test_api/test_odpchain/test_agents/test_dataengineering/test_tools/test_wrappers.py'
# modify_file(file_path)