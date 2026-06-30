import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.dataframe_supplier.df_suppy import *

class TestDfSupply(unittest.TestCase):

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.dataframe_supplier.df_suppy.MongoFactory')
    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.dataframe_supplier.df_suppy.MongoConnector')
    @patch('pandas.read_feather')
    def test_get_head(self, mock_read_feather, mock_MongoConnector, mock_MongoFactory):
        # Mock DataFrame
        mock_df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [5, 4, 3, 2, 1]
        })
        mock_read_feather.return_value = mock_df

        # Mock session
        mock_session = MagicMock()

        # Mock MongoFactory to return the required document
        mock_cache_instance = mock_MongoFactory.return_value
        mock_chats_instance = mock_MongoFactory.return_value

        mock_chats_instance.get_by_id.return_value = (True, {"cwf": {"source_id": "source_id_value"}, "user_id": "mock_user_id"})
        mock_cache_instance.get_by_fields.return_value = (True, {"feather_file_path": "mock_path"})

        # Call the function
        result = get_head('mock_chat_id', mock_session)

        # Validate the result
        expected_result = str(mock_df.head(5).to_markdown())
        self.assertEqual(result, expected_result)

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.dataframe_supplier.df_suppy.MongoFactory')
    def test_get_datatype(self, mock_MongoFactory):
        # Mock MongoFactory to return the required document
        mock_cache_instance = mock_MongoFactory.return_value
        mock_chats_instance = mock_MongoFactory.return_value

        mock_chats_instance.get_by_id.return_value = (True, {"cwf": {"source_id": "source_id_value"}, "user_id": "mock_user_id"})
        mock_cache_instance.get_by_fields.return_value = (True, {"metadata": {"column_information": {"datatypes": {"col1": "int", "col2": "float"}}}})

        # Call the function
        result = get_datatype('mock_chat_id')

        # Validate the result
        expected_result = "{'col1': 'int', 'col2': 'float'}"
        self.assertEqual(result, expected_result)

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.dataframe_supplier.df_suppy.MongoFactory')
    @patch('pandas.read_feather')
    def test_get_columns(self, mock_read_feather, mock_MongoFactory):
        # Mock DataFrame
        mock_df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [5, 4, 3, 2, 1]
        })
        mock_read_feather.return_value = mock_df

        # Mock session
        mock_session = MagicMock()

        # Mock MongoFactory to return the required document
        mock_cache_instance = mock_MongoFactory.return_value
        mock_chats_instance = mock_MongoFactory.return_value

        mock_chats_instance.get_by_id.return_value = (True, {"cwf": {"source_id": "source_id_value"}, "user_id": "mock_id"})
        mock_cache_instance.get_by_fields.return_value = (True, {"feather_file_path": "mock_path"})

        # Call the function
        result = get_columns('mock_chat_id', mock_session)

        # Validate the result
        expected_columns = ['A', 'B']
        self.assertEqual(result, expected_columns)

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.dataframe_supplier.df_suppy.MongoFactory')
    @patch('pandas.read_feather')
    def test_get_metadata(self, mock_read_feather, mock_MongoFactory):
        # Mock DataFrame
        mock_df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [5, 4, 3, 2, 1]
        })
        mock_read_feather.return_value = mock_df

        # Mock session
        mock_session = MagicMock()

        # Mock MongoFactory to return the required document
        mock_cache_instance = mock_MongoFactory.return_value
        mock_chats_instance = mock_MongoFactory.return_value

        mock_chats_instance.get_by_id.return_value = (True, {"cwf": {"source_id": "source_id_value"}, "user_id": "mock_user_id"})
        mock_cache_instance.get_by_fields.return_value = (True, {"feather_file_path": "mock_path"})

        # Call the function
        result = get_metadata('mock_chat_id', mock_session)

        # Validate the result
        expected_result = (
            "CREATE TABLE df (\n"
            "    A INTEGER,\n"
            "    B INTEGER\n"
            ");"
        )
        self.assertEqual(result, expected_result)

    def test_generate_create_table_statement(self):
        # Mock DataFrame
        mock_df = pd.DataFrame({
            'A': pd.Series([1, 2, 3], dtype='int64'),
            'B': pd.Series([1.1, 2.2, 3.3], dtype='float64'),
            'C': pd.Series([True, False, True], dtype='bool'),
            'D': pd.Series(['2023-08-28', '2023-08-29', '2023-08-30'], dtype='datetime64[ns]'),
            'E': pd.Series(['text1', 'text2', 'text3'], dtype='object')
        })

        # Call the function
        result = generate_create_table_statement(mock_df, 'test_table')

        # Validate the result
        expected_result = (
            "CREATE TABLE test_table (\n"
            "    A INTEGER,\n"
            "    B FLOAT,\n"
            "    C BOOLEAN,\n"
            "    D TIMESTAMP,\n"
            "    E TEXT\n"
            ");"
        )
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
