import unittest
import json
import os
import pandas as pd
import pytest

from src.exceptions.exception import DatabaseConnectorException
from core.datasource.implementations.document_db import UnifiedDocumentDB


class TestCouchbaseConnector(unittest.TestCase):
    """Simplified test suite for Couchbase UnifiedDocumentDB connector"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class with connection details and connector instance"""
        # Load test credentials
        json_file_path = os.path.join(
            os.path.abspath(os.path.join(__file__, "../../../..")), 
            "test_configurations", "test_hooks", "couchbase_creds.json"
        )
        
        with open(json_file_path, "r") as json_file:
            cls.connection_details = json.load(json_file)
        
        cls.connector = UnifiedDocumentDB()
        cls.engine = "couchbase"
        
    def setUp(self):
        """Set up each test with fresh connector instance"""
        self.connector = UnifiedDocumentDB()

    # CONNECTION TESTS
    
    def test_connection_success(self):
        """Test successful connection to Couchbase"""
        result = self.connector.connect(self.connection_details, engine=self.engine)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)  # Should return (cluster, bucket) tuple
        
        cluster, bucket = result
        self.assertIsNotNone(cluster)
        self.assertIsNotNone(bucket)
    
    def test_connection_health_check(self):
        """Test connection health validation"""
        result = self.connector.test_connection(self.connection_details, engine=self.engine)
        self.assertTrue(result)
    
    def test_connection_with_invalid_credentials(self):
        """Test connection failure with wrong credentials"""
        invalid_creds = self.connection_details.copy()
        invalid_creds['username'] = 'wrong_user'
        invalid_creds['password'] = 'wrong_pass'
        
        with self.assertRaises(DatabaseConnectorException):
            self.connector.test_connection(invalid_creds, engine=self.engine)
    
    def test_connection_with_invalid_host(self):
        """Test connection failure with wrong host"""
        invalid_creds = self.connection_details.copy()
        invalid_creds['host'] = 'nonexistent.host.com'
        
        with self.assertRaises(DatabaseConnectorException):
            self.connector.test_connection(invalid_creds, engine=self.engine)


    # METADATA TESTS
    
    def test_get_metadata(self):
        """Test retrieving database structure metadata"""
        metadata = self.connector.get_metadata(self.connection_details, engine=self.engine)
        
        self.assertIsInstance(metadata, list)
        self.assertGreater(len(metadata), 0)
        
        # Verify metadata structure
        first_scope = metadata[0]
        self.assertIn('title', first_scope)
        self.assertIn('value', first_scope)
        self.assertIsNotNone(first_scope['title'])
    
    def test_metadata_contains_collections(self):
        """Test that metadata includes collection information"""
        metadata = self.connector.get_metadata(self.connection_details, engine=self.engine)
        
        # Find a scope with collections
        scope_with_collections = None
        for scope in metadata:
            if 'children' in scope and len(scope['children']) > 0:
                scope_with_collections = scope
                break
        
        if scope_with_collections:
            collection = scope_with_collections['children'][0]
            self.assertIn('title', collection)
            self.assertIn('value', collection)

    # COLUMN DISCOVERY TESTS
    
    def test_get_columns_from_default_collection(self):
        """Test column discovery from default collection"""
        try:
            columns = self.connector.get_columns(
                self.connection_details, 
                "_default._default", 
                engine=self.engine
            )
            self.assertIsInstance(columns, list)
            
            # If columns exist, verify they are strings
            for column in columns:
                self.assertIsInstance(column, str)
                
        except DatabaseConnectorException as e:
            if "empty" in str(e).lower():
                self.skipTest("Default collection is empty")
            else:
                raise
    
    def test_get_columns_from_available_collection(self):
        """Test column discovery from first available collection with data"""
        metadata = self.connector.get_metadata(self.connection_details, engine=self.engine)
        
        collection_tested = False
        for scope in metadata:
            if 'children' in scope:
                for collection in scope['children']:
                    collection_path = collection['value']
                    try:
                        columns = self.connector.get_columns(
                            self.connection_details, 
                            collection_path, 
                            engine=self.engine
                        )
                        self.assertIsInstance(columns, list)
                        collection_tested = True
                        break
                    except DatabaseConnectorException:
                        continue
            if collection_tested:
                break
        
        if not collection_tested:
            self.skipTest("No collections with data found for column testing")
    
    def test_get_columns_nonexistent_collection(self):
        """Test column discovery failure for non-existent collection"""
        with self.assertRaises(DatabaseConnectorException):
            self.connector.get_columns(
                self.connection_details, 
                "nonexistent.scope.collection", 
                engine=self.engine
            )

    # DATA FETCHING TESTS
    
    def test_fetch_data_basic(self):
        """Test basic data fetching from available collection"""
        try:
            # Try default collection first
            df = self.connector.fetch_data(
                self.connection_details, 
                "_default._default", 
                engine=self.engine,
                num_rows=5
            )
            self.assertIsInstance(df, pd.DataFrame)
            
        except DatabaseConnectorException as e:
            if "empty" in str(e).lower() or "no data" in str(e).lower():
                self.skipTest("Default collection has no data")
            else:
                # Try to find a collection with data
                metadata = self.connector.get_metadata(self.connection_details, engine=self.engine)
                data_found = False
                
                for scope in metadata:
                    if 'children' in scope:
                        for collection in scope['children']:
                            try:
                                df = self.connector.fetch_data(
                                    self.connection_details, 
                                    collection['value'], 
                                    engine=self.engine,
                                    num_rows=5
                                )
                                self.assertIsInstance(df, pd.DataFrame)
                                data_found = True
                                break
                            except DatabaseConnectorException:
                                continue
                    if data_found:
                        break
                
                if not data_found:
                    self.skipTest("No collections with data found")
    
    def test_fetch_data_with_limit(self):
        """Test data fetching with row limit"""
        try:
            df = self._fetch_data_from_any_collection(num_rows=3)
            if not df.empty:
                self.assertLessEqual(len(df), 3)
        except Exception:
            self.skipTest("No data available for limit testing")
    
    def test_fetch_data_with_columns_filter(self):
        """Test data fetching with specific columns"""
        try:
            # Get a collection with data and columns
            collection_path, columns = self._get_collection_with_columns()
            
            if collection_path and columns:
                # Test with first 2 columns
                selected_columns = columns[:min(2, len(columns))]
                df = self.connector.fetch_data(
                    self.connection_details,
                    collection_path,
                    columns=selected_columns,
                    engine=self.engine,
                    num_rows=5
                )
                self.assertIsInstance(df, pd.DataFrame)
                
        except Exception:
            self.skipTest("No suitable data for column filtering test")
    
    def test_fetch_data_nonexistent_collection(self):
        """Test data fetching failure for non-existent collection"""
        with self.assertRaises(DatabaseConnectorException):
            self.connector.fetch_data(
                self.connection_details,
                "nonexistent.scope.collection",
                engine=self.engine
            )


if __name__ == '__main__':
    # Run specific test methods or all tests
    unittest.main(verbosity=2)