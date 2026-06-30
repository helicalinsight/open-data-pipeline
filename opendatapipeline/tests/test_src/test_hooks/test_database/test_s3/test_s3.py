import json
import os
import unittest
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO

from core.datasource.implementations.s3 import S3
from src.exceptions.exception import *

test_configs_dir = os.path.join(os.path.abspath(os.path.join(__file__, "../../../..")), "test_configurations", "test_hooks")
local_json_path = os.path.join(test_configs_dir, "s3_creds-local.json")
default_json_path = os.path.join(test_configs_dir, "s3_creds.json")

json_file_path = os.getenv("AOD_S3_TEST_CREDS_PATH")
if not json_file_path:
    if os.path.exists(local_json_path):
        json_file_path = local_json_path
    else:
        json_file_path = default_json_path
json_file_path = os.path.abspath(json_file_path)

with open(json_file_path, "r") as json_file:
    connection_details = json.load(json_file)


class TestS3(unittest.TestCase):

    @patch("boto3.client")
    def test_connect(self, mock_boto_client):
        mock_boto_client.return_value = MagicMock()
        actual_result = S3().connect(connection_details)
        self.assertIsNotNone(actual_result)

    def test_connect_missing_credentials(self):
        copied_details = connection_details.copy()
        copied_details.pop("aws_access_key")
        with pytest.raises(DatabaseConnectorException) as exc_info:
            S3().connect(copied_details)
        assert "Missing one or more required AWS credentials" in str(exc_info.value)

    @patch.object(S3, "connect")
    def test_test_connection(self, mock_connect):
        mock_connect.return_value = MagicMock()
        result = S3().test_connection(connection_details)
        self.assertTrue(result)

    @patch.object(S3, "connect")
    @patch("pandas.read_csv")
    def test_fetch_data_csv(self, mock_read_csv, mock_connect):
        sample_csv_content = b"col1,col2\n1,2\n3,4"
        mock_connect.return_value.get_object.return_value = {"Body": BytesIO(sample_csv_content)}
        mock_read_csv.return_value = pd.DataFrame({"col1": [1, 3], "col2": [2, 4]})        
        catalog = "2017_Order_Data.csv"
        result = S3().fetch_data(connection_details, catalog)        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)

    @patch.object(S3, "connect")
    @patch("pandas.read_parquet")
    def test_fetch_data_iceberg(self, mock_read_parquet, mock_connect):
        mock_s3_client = MagicMock()
        mock_body = MagicMock()
        mock_body.read.return_value = b"parquet binary content"
        mock_s3_client.get_object.return_value = {"Body": mock_body}
        mock_connect.return_value = mock_s3_client
        mock_read_parquet.return_value = pd.DataFrame({"a": [1]})
        catalog = "iceberg/data/sample.parquet"
        result = S3().fetch_data(connection_details, catalog)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
    
    @patch.object(S3, "connect")
    def test_fetch_data_with_non_existing_table(self, mock_connect):
        mock_connect.return_value.get_object.side_effect = Exception(
            "An error occurred (NoSuchKey) when calling the GetObject operation: The specified key does not exist."
        )
        catalog = "2018_Order_Data.csv"
        with pytest.raises(DatabaseConnectorException) as test_function:
            S3().fetch_data(connection_details, catalog)
        self.assertEqual(
            "Failed to fetch S3 data: An error occurred (NoSuchKey) when calling the GetObject operation: The specified key does not exist.",
            str(test_function.value)
        )

    @patch.object(S3, "connect")
    def test_get_metadata(self, mock_connect):
        mock_connect.return_value.list_objects_v2.return_value = {
            "Contents": [{"Key": "2017_Order_Data.csv"}]
        }
        result = S3().get_metadata(connection_details)
        self.assertEqual(result[0]["title"], "2017_Order_Data.csv")

    @patch.object(S3, "fetch_data")
    def test_get_columns(self, mock_fetch_data):
        mock_fetch_data.return_value = pd.DataFrame({"a": [1], "b": [2]})
        db_name = "2017_Order_Data.csv"
        result = S3().get_columns(connection_details, db_name)
        self.assertTrue(isinstance(result, list))
        self.assertGreater(len(result), 0)


if __name__ == '__main__':
    unittest.main()
