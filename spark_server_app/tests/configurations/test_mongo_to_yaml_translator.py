import unittest
from spark_server.configurations.mongo_to_yaml_translator import MongoToYamlTranslator
from unittest.mock import patch
import yaml
import pytest
from spark_server.exceptions.exceptions import *
from bson import ObjectId


class TestMongoToYamlTranslator(unittest.TestCase):

    def test_get_chat(self):
        actual_result = MongoToYamlTranslator().get_chat("65cb43f2007a5f38718b9d6a")
        expected_result = {'_id': ObjectId('65cb43f2007a5f38718b9d6a'), 'user_id': '6619156aa5f4c5c1b01e4d07', 'chat_id': '665e937aaea87247ea567131', 'pipeline': [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'source_id': '662bb3d788e28e8af8679eb7'}, 'output': None}, {'id': '0f7a7b91-be3a-4a6b-a62e-f1ed419d830c', 'step': 1, 'status': 'PASS', 'function': 'when_otherwise', 'parameters': {'groups': [{'query': "SELECT datediff('month', DATE '1992-09-15', DATE '1992-11-14') FROM df;"}]}, 'output': None}], 'next': []}
        self.assertEqual(actual_result, expected_result)

    def test_get_chat_wrong_parameters(self):
        with pytest.raises(UtilsException) as test_function:      
            MongoToYamlTranslator().get_chat("65cb43f2007a5f38718b3111")
        self.assertEqual("Chat history not found.", str(test_function.value))

    def test_get_chat_history(self):
        actual_result = MongoToYamlTranslator().get_chat_history("65cb43f2007a5f38718b9d6a")
        expected_result = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'source_id': '662bb3d788e28e8af8679eb7'}, 'output': None}, {'id': '0f7a7b91-be3a-4a6b-a62e-f1ed419d830c', 'step': 1, 'status': 'PASS', 'function': 'when_otherwise', 'parameters': {'groups': [{'query': "SELECT datediff('month', DATE '1992-09-15', DATE '1992-11-14') FROM df;"}]}, 'output': None}]
        self.assertEqual(actual_result, expected_result)

    def test_get_chat_history(self):
        actual_result = MongoToYamlTranslator().get_chat_history("65cb43f2007a5f38718b9d6b")
        expected_result = []
        self.assertEqual(actual_result, expected_result)

    def test_get_chat_history_wrong_parameters(self):
        with pytest.raises(UtilsException) as test_function:   
            MongoToYamlTranslator().get_chat_history("65cb43f2007a5f38718b3111")
        self.assertEqual("Failed to get chat history.", str(test_function.value))

    def test_get_code(self):
        actual_result = MongoToYamlTranslator().get_code("65cb43f2007a5f38718b9d6c")
        expected_result = 'print("hi")'
        self.assertEqual(actual_result, expected_result)

    def test_get_code_wrong_parameters(self):
        with pytest.raises(UtilsException) as test_function:
            MongoToYamlTranslator().get_code("65cb43f2007a5f38718b3111")
        expected_result = 'print("hi")'
        self.assertEqual("Failed to get code.", str(test_function.value))

    def test_filter_for_status_pass(self):
        chat_history = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'source_id': '662bb3d788e28e8af8679eb7'}, 'output': None}, {'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'FAIL', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'source_id': '662bb3d788e28e8af8679eb7'}, 'output': None}, {'id': '0f7a7b91-be3a-4a6b-a62e-f1ed419d830c', 'step': 1, 'status': 'PASS', 'function': 'when_otherwise', 'parameters': {'groups': [{'query': "SELECT datediff('month', DATE '1992-09-15', DATE '1992-11-14') FROM df;"}]}, 'output': None}]
        actual_result = MongoToYamlTranslator().filter_for_status_pass(chat_history)
        expected_result = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'source_id': '662bb3d788e28e8af8679eb7'}, 'output': None}, {'id': '0f7a7b91-be3a-4a6b-a62e-f1ed419d830c', 'step': 1, 'status': 'PASS', 'function': 'when_otherwise', 'parameters': {'groups': [{'query': "SELECT datediff('month', DATE '1992-09-15', DATE '1992-11-14') FROM df;"}]}, 'output': None}]
        self.assertEqual(actual_result, expected_result)

    def test_filter_for_status_pass_without_status(self):
        chat_history = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'source_id': '662bb3d788e28e8af8679eb7'}, 'output': None}]
        actual_result = MongoToYamlTranslator().filter_for_status_pass(chat_history)
        expected_result = []
        self.assertEqual(actual_result, expected_result)

    def test_filter_for_status_pass_with_empty_chat(self):
        chat_history = [{}]
        actual_result = MongoToYamlTranslator().filter_for_status_pass(chat_history)
        expected_result = []
        self.assertEqual(actual_result, expected_result)
    
    def test_update_to_df_id(self):
        chat_history = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'source_id': '662bb3d788e28e8af8679eb7'}}]
        actual_result = MongoToYamlTranslator().update_to_df_id(chat_history)
        expected_result = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}}]
        self.assertEqual(actual_result, expected_result)
        
    def test_remove_output_null(self):
        chat_history = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}, 'output': None}]
        actual_result = MongoToYamlTranslator().remove_output_null(chat_history)
        expected_result = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}}]
        self.assertEqual(actual_result, expected_result)

    def test_remove_output_null_with_output_not_null(self):
        chat_history = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}, 'output': "test"}]
        actual_result = MongoToYamlTranslator().remove_output_null(chat_history)
        expected_result = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}, 'output': "test"}]
        self.assertEqual(actual_result, expected_result)

    def test_remove_output_null_without_output(self):
        chat_history = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}}]
        actual_result = MongoToYamlTranslator().remove_output_null(chat_history)
        expected_result = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}}]
        self.assertEqual(actual_result, expected_result)

    def test_remove_output_null_with_empty_chat(self):
        chat_history = [{}]
        actual_result = MongoToYamlTranslator().remove_output_null(chat_history)
        expected_result = [{}]
        self.assertEqual(actual_result, expected_result)

    def test_remove_unnecessary_keys(self):
        chat_history = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}}]
        actual_result = MongoToYamlTranslator().remove_unnecessary_keys(chat_history)
        expected_result = [{'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}}]
        self.assertEqual(actual_result, expected_result)

    def test_remove_unnecessary_keys_without_id(self):
        chat_history = [{'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}}]
        actual_result = MongoToYamlTranslator().remove_unnecessary_keys(chat_history)
        expected_result = [{'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}}]
        self.assertEqual(actual_result, expected_result)

    def test_remove_unnecessary_keys_without_step(self):
        chat_history = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}}]
        actual_result = MongoToYamlTranslator().remove_unnecessary_keys(chat_history)
        expected_result = [{'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}}]
        self.assertEqual(actual_result, expected_result)

    def test_remove_unnecessary_keys_without_status(self):
        chat_history = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}}]
        actual_result = MongoToYamlTranslator().remove_unnecessary_keys(chat_history)
        expected_result = [{'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}}]
        self.assertEqual(actual_result, expected_result)

    def test_remove_unnecessary_keys_without_id_step_status(self):
        chat_history = [{'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}}]
        actual_result = MongoToYamlTranslator().remove_unnecessary_keys(chat_history)
        expected_result = [{'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'df_id': '662bb3d788e28e8af8679eb7'}}]
        self.assertEqual(actual_result, expected_result)
    
    def test_remove_unnecessary_keys_with_empty_chat(self):
        chat_history = [{}]
        actual_result = MongoToYamlTranslator().remove_unnecessary_keys(chat_history)
        expected_result = [{}]
        self.assertEqual(actual_result, expected_result)

    @patch('core.mongo.mongo_factory.MongoFactory.get_by_user_id_job_id')
    def test_get_chat_history_exception(self, mock_get_by_user_id_job_id):
        # Mock the side effect of mongo_chats.get_by_user_id_job_id to raise an exception
        mock_get_by_user_id_job_id.side_effect = Exception("Database connection error")
        with pytest.raises(UtilsException) as test_function:      
            MongoToYamlTranslator().get_chat_history('65cb43f2007a5f38718b3111')
        self.assertEqual("Failed to get chat history.", str(test_function.value))

    def test_convert_to_yaml(self):
        chat = {'message': 'Hello'}
        yaml = MongoToYamlTranslator().convert_to_yaml(chat)
        self.assertEqual(yaml, "message: Hello\n")

    @patch('spark_server.configurations.mongo_to_yaml_translator.yaml.dump')
    def test_convert_to_yaml_exception(self, mock_yaml_dump):
        # Mock the side effect of yaml.dump to raise an exception
        mock_yaml_dump.side_effect = Exception("Error converting to YAML")
        with pytest.raises(UtilsException) as test_function:      
            MongoToYamlTranslator().convert_to_yaml({'message': 'Hello'})
        self.assertEqual("Failed to convert to yaml.", str(test_function.value))
    
    def test_convert_duckdb_to_sparksql_date(self):
        duckdb_query = "SELECT date_add(DATE '1992-09-15', INTERVAL 2 MONTH) from df"
        sparksql_query = MongoToYamlTranslator().convert_duckdb_to_sparksql(duckdb_query)
        self.assertEqual(sparksql_query, "SELECT DATE_ADD(CAST('1992-09-15' AS DATE), INTERVAL '2' MONTH) FROM df")

    def test_convert_duckdb_to_sparksql_limit(self):
        duckdb_query = "SELECT * from df limit 1000"
        sparksql_query = MongoToYamlTranslator().convert_duckdb_to_sparksql(duckdb_query)
        self.assertEqual(sparksql_query, "SELECT * FROM df LIMIT 1000")

    def test_convert_duckdb_to_sparksql_date_diff(self):
        duckdb_query = "SELECT datediff('month', DATE '1992-09-15', DATE '1992-11-14') FROM df"
        sparksql_query = MongoToYamlTranslator().convert_duckdb_to_sparksql(duckdb_query)
        self.assertEqual(sparksql_query,  "SELECT DATEDIFF(MONTH, CAST('1992-09-15' AS DATE), CAST('1992-11-14' AS DATE)) FROM df")

    @patch('spark_server.configurations.mongo_to_yaml_translator.sqlglot.transpile')
    def test_convert_duckdb_to_sparksql_exception(self, mock_transpile):
        # Mock the side effect of sqlglot.transpile to raise an exception
        mock_transpile.side_effect = Exception("Error converting query from DuckDB to SparkSQL")
        with pytest.raises(UtilsException) as test_function:      
            MongoToYamlTranslator().convert_duckdb_to_sparksql("SELECT * FROM table")
        self.assertEqual("Failed to convert duckdb to spark sql.", str(test_function.value))

    def test_apply_sql_glot(self):
        chat_history = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'source_id': '662bb3d788e28e8af8679eb7'}, 'output': None}, {'id': '0f7a7b91-be3a-4a6b-a62e-f1ed419d830c', 'step': 1, 'status': 'PASS', 'function': 'when_otherwise', 'parameters': {'groups': [{'query': "SELECT datediff('month', DATE '1992-09-15', DATE '1992-11-14') FROM df;"}]}, 'output': None}]
        actual_chat_history = MongoToYamlTranslator().apply_sql_glot(chat_history)
        expected_chat_history = [{'id': 'eb0405bc-b99a-4cda-8802-12506c631ba7', 'step': 0, 'status': 'PASS', 'function': 'read_files', 'parameters': {'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)', 'source_id': '662bb3d788e28e8af8679eb7'}, 'output': None}, {'id': '0f7a7b91-be3a-4a6b-a62e-f1ed419d830c', 'step': 1, 'status': 'PASS', 'function': 'when_otherwise', 'parameters': {'groups': [{'query': "SELECT DATEDIFF(MONTH, CAST('1992-09-15' AS DATE), CAST('1992-11-14' AS DATE)) FROM df"}]}, 'output': None}]
        self.assertEqual(actual_chat_history, expected_chat_history)

    @patch.object(MongoToYamlTranslator, 'convert_duckdb_to_sparksql')
    def test_apply_sql_glot_exception(self, mock_convert_duckdb_to_sparksql):
        # Mock the side effect of convert_duckdb_to_sparksql to raise an exception
        mock_convert_duckdb_to_sparksql.side_effect = Exception("Error converting query from DuckDB to SparkSQL")
        chat_history = [
            {'function': 'when_otherwise', 'parameters': {'groups': [{'query': 'SELECT * FROM table1'}, {'query': 'SELECT * FROM table2'}]}},
            {'function': 'sql', 'parameters': {'groups': [{'query': 'SELECT * FROM table3'}]}}
        ]
        with pytest.raises(UtilsException) as test_function:
            MongoToYamlTranslator().apply_sql_glot(chat_history)
        self.assertEqual("Failed to apply sql glot.", str(test_function.value))

    def test_process(self):
        actual_result = MongoToYamlTranslator().process("65cb43f2007a5f38718b9d6a")
        expected_result = [{'function': 'read_files', 'parameters': {'df_id': '662bb3d788e28e8af8679eb7', 'file_id': 'aa9ef98e-438c-48ed-9622-19f3a94b3106', 'file_name': 'Dummy_Data (1)'}}, {'function': 'when_otherwise', 'parameters': {'groups': [{'query': "SELECT DATEDIFF(MONTH, CAST('1992-09-15' AS DATE), CAST('1992-11-14' AS DATE)) FROM df"}]}}]
        self.assertEqual(yaml.safe_load(actual_result), expected_result)


if __name__ == '__main__':
    unittest.main()
