import unittest
from unittest.mock import MagicMock, patch
from bson import ObjectId
import pandas as pd
from src.api.services.rerun.utils import CreateDFDictionary, DFInformation, ReRunUtilities

from src.models.connector import MongoConnector

mongo_client = MongoConnector().client
session = mongo_client._Database__client.start_session()

class TestCreateDFDictionary(unittest.TestCase):
    @unittest.skip("No valid test data to test this when we pass all source, chat and user id for getting cache")
    def test_create_success(self):
        chat_id = "66729ec22ee1491c32b05b53"
        result = CreateDFDictionary(session).create(chat_id)
        
        self.assertIsNotNone(result['66729ece2ee1491c32b05b54'])

if __name__ == '__main__':
    unittest.main()

class TestDFInformation(unittest.TestCase):
    def setUp(self):
        """Set up the test data."""
        self.df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        self.df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})
        
        self.config_dict = {
            'source_id_1': {'df': self.df1, 'alias': 'alias1'},
            'source_id_2': {'df': self.df2, 'alias': 'alias2'}
        }
        
        self.df_info = DFInformation(config_dict=self.config_dict)

    def test_get_by_source_id(self):
        """Test retrieving a DataFrame by source ID."""
        result_df = self.df_info.get(id='source_id_1')
        pd.testing.assert_frame_equal(result_df, self.df1)

    def test_get_by_alias(self):
        """Test retrieving a DataFrame by alias."""
        result_df = self.df_info.get(alias='alias2')
        pd.testing.assert_frame_equal(result_df, self.df2)

    def test_get_by_source_id_and_alias_match(self):
        """Test retrieving a DataFrame with matching source ID and alias."""
        result_df = self.df_info.get(id='source_id_1', alias='alias1')
        pd.testing.assert_frame_equal(result_df, self.df1)

    def test_get_by_source_id_and_alias_mismatch(self):
        """Test retrieving a DataFrame with mismatched source ID and alias."""
        with self.assertRaises(ValueError):
            self.df_info.get(id='source_id_1', alias='alias2')

    def test_get_unregistered_source_id(self):
        """Test retrieving a DataFrame with an unregistered source ID."""
        with self.assertRaises(ValueError):
            self.df_info.get(id='source_id_unregistered')

    def test_get_unregistered_alias(self):
        """Test retrieving a DataFrame with an unregistered alias."""
        with self.assertRaises(ValueError):
            self.df_info.get(alias='alias_unregistered')

    def test_get_missing_parameters(self):
        """Test retrieval with neither source ID nor alias."""
        with self.assertRaises(ValueError):
            self.df_info.get()

    def test_get_id_by_alias(self):
        """Test retrieving the source ID by alias."""
        result_id = self.df_info.get_id_by_alias('alias1')
        self.assertEqual(result_id, 'source_id_1')

    def test_get_id_by_alias_not_found(self):
        """Test retrieving the source ID by alias when alias is not found."""
        result_id = self.df_info.get_id_by_alias('alias_unregistered')
        self.assertIsNone(result_id)

if __name__ == '__main__':
    unittest.main()


class TestReRunUtilities(unittest.TestCase):
    def setUp(self):
        """Set up test data and an instance of ReRunUtilities."""
        self.df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        self.df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})
        
        self.data_dict = {
            'source_id_1': {'df': self.df1, 'alias': 'alias1'},
            'source_id_2': {'df': self.df2, 'alias': 'alias2'}
        }
        
        self.utilities = ReRunUtilities()

    def test_update_with_both_alias_and_source_id(self):
        """Test updating the config when both alias and source ID are provided and match."""
        updated_dict = self.utilities.update_configurations(self.data_dict, alias='alias1', source_id='source_id_1', df=self.df2)
        pd.testing.assert_frame_equal(updated_dict['source_id_1']['df'], self.df2)

    def test_update_with_mismatched_alias_and_source_id(self):
        """Test updating the config when both alias and source ID are provided but do not match."""
        with self.assertRaises(ValueError):
            self.utilities.update_configurations(self.data_dict, alias='alias2', source_id='source_id_1', df=self.df2)

    def test_update_with_only_alias(self):
        """Test updating the config when only alias is provided."""
        updated_dict = self.utilities.update_configurations(self.data_dict, alias='alias1', df=self.df2)
        pd.testing.assert_frame_equal(updated_dict['source_id_1']['df'], self.df2)

    # @patch('src.api.services.rerun.utils.ObjectId')
    # def test_update_with_new_alias(self, mock_objectid):
    #     """Test creating a new entry when the alias is not found and source ID is not provided."""
    #     mock_objectid.return_value = ObjectId("507f1f77bcf86cd799439011")
    #     updated_dict = self.utilities.update_configurations(self.data_dict, alias='new_alias', df=self.df2)
    #     self.assertIn(str(mock_objectid.return_value), updated_dict)
    #     pd.testing.assert_frame_equal(updated_dict[str(mock_objectid.return_value)]['df'], self.df2)
    #     self.assertEqual(updated_dict[str(mock_objectid.return_value)]['alias'], 'new_alias')

    def test_update_with_only_source_id(self):
        """Test updating the config when only source ID is provided."""
        updated_dict = self.utilities.update_configurations(self.data_dict, source_id='source_id_1', df=self.df2)
        pd.testing.assert_frame_equal(updated_dict['source_id_1']['df'], self.df2)

    @patch.object(ReRunUtilities, 'generate_random_key')
    def test_update_with_new_source_id(self, mock_generate_random_key):
        """Test creating a new entry when the source ID is not found and alias is not provided."""
        mock_generate_random_key.return_value = 'random_alias'
        updated_dict = self.utilities.update_configurations(self.data_dict, source_id='new_source_id', df=self.df2, intent_name='intent')
        self.assertIn('new_source_id', updated_dict)
        pd.testing.assert_frame_equal(updated_dict['new_source_id']['df'], self.df2)
        self.assertEqual(updated_dict['new_source_id']['alias'], 'random_alias')

    def test_generate_random_key(self):
        """Test generating a random key with a given prefix."""
        prefix = 'test'
        random_key = self.utilities.generate_random_key(prefix)
        self.assertTrue(random_key.startswith(prefix + '_'))
        self.assertEqual(len(random_key), len(prefix) + 7)  # prefix_ + 6 random characters

    def test_update_with_missing_parameters(self):
        """Test updating the config when neither alias nor source ID is provided."""
        with self.assertRaises(ValueError):
            self.utilities.update_configurations(self.data_dict, df=self.df2)

if __name__ == '__main__':
    unittest.main()