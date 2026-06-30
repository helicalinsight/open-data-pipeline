import unittest
from spark_server.database_connectors.postgres import Postgres
from spark_server.exceptions.exceptions import *
import os
import pytest
from test_setup import TestSetup
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType
from datetime import datetime


@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
class TestPostgres(unittest.TestCase):
    # creating the instance of the class Postgres
    @classmethod
    def setUpClass(cls):
        cls.spark = TestSetup.set_up_spark()
        cls.postgres = Postgres(cls.spark)
        cls.connection_id = {
            "654879fe42a09b96f228302c": {
                "type": "database",
                "details": {
                    "type": "postgres",
                    "sourceName": "Postgres Connector 2",
                    "host": "57.128.161.235",
                    "port": "5432",
                    "username": "airflow",
                    "password": "Helical@1234",
                    "database": "sakila"
                }
            },
            "654879fe42a09b96f228302d": {
                "type": "database",
                "details": {
                    "type": "postgres",
                    "sourceName": "Postgres Connector 3",
                    "host": "57.128.161.235",
                    "port": "5432",
                    "username": "airflow",
                    "password": "Helical@1234",
                    "database": "sakila",
                    "connection_pool": {
                        "pandas_pooling": {
                            "pool_size": "10",
                            "max_overflow": "20",
                            "pool_timeout": "30",
                            "pool_recycle": "1800",
                        },
                        "spark_pooling": {
                            "dbcp.maxTotal": "9",
                            "dbcp.maxIdle": "18",
                            "dbcp.maxWaitMillis": "35000",
                            "dbcp.maxConnLifetimeMillis": "1850000",
                        }
                    }
                }
            }
        }

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_connect(self):
        config = self.postgres.connect(self.connection_id["654879fe42a09b96f228302c"])
        self.assertIsNotNone(config["url"])

    def test_test_connection(self):
        connection = self.postgres.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor", "df_id": "65dc3fb832b5b2a5665841fb"}
        test_result = self.postgres.test_connection(config, connection)
        self.assertEqual(True, test_result)

    def test_fetch_data(self):
        connection = self.postgres.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor", "df_id": "65dc3fb832b5b2a5665841fb"}
        result = self.postgres.fetch_data(config, connection)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_columns(self):
        connection = self.postgres.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor", "columns": ["first_name", "last_name"], "df_id": "65dc3fb832b5b2a5665841fb"}
        result = self.postgres.fetch_data(config, connection)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)
        self.assertEqual(["first_name", "last_name"], result["df"].columns)

    def test_fetch_data_with_custom_config_dbtable(self):
        connection = self.postgres.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor", "df_id": "65dc3fb832b5b2a5665841fb"}
        custom_config = {"dbtable": "actor"}
        result = self.postgres.fetch_data(config, connection, custom_config)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_custom_config_query(self):
        connection = self.postgres.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor", "df_id": "65dc3fb832b5b2a5665841fb"}
        custom_config = {"query": "select actor_id from actor"}
        result = self.postgres.fetch_data(config, connection, custom_config)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_custom_config_dbtable_query(self):
        connection = self.postgres.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor", "df_id": "65dc3fb832b5b2a5665841fb"}
        custom_config = {"dbtable": "actor", "query": "select actor_id from actor"}
        result = self.postgres.fetch_data(config, connection, custom_config)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_fetch_data_with_invalid_table_in_custom_config(self):
        connection = self.postgres.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "public.actor", "df_id": "65dc3fb832b5b2a5665841fb"}
        custom_config = {"dbtable": "actor_1"}
        with pytest.raises(DatabaseConnectionException) as test_function:
            self.postgres.fetch_data(config, connection, custom_config)
        self.assertEqual("Failed to fetch the data from database.", str(test_function.value))

    def test_fetch_data_with_connection_pool(self):
        connection = self.postgres.connect(self.connection_id["654879fe42a09b96f228302d"])
        config = {"connection_id": "654879fe42a09b96f228302d", "table_name": "public.actor", "df_id": "65dc3fb832b5b2a5665841fb"}
        result = self.postgres.fetch_data(config, connection)["65dc3fb832b5b2a5665841fb"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_write_data(self):
        """
        Test writing data to Postgres database table
        """
        connection = self.postgres.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "actor1", "df_id": "65dc3fb832b5b2a5665841fb"}
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("first_name", StringType(), True),
            StructField("last_name", StringType(), True),
            StructField("timestamp", TimestampType(), True)
        ])
        test_data = [
            (1, "Chandler", "Bing", datetime.strptime("2024-02-15 04:34:33", "%Y-%m-%d %H:%M:%S")),
            (2, "Rachel", "Green", datetime.strptime("2024-02-16 06:52:11", "%Y-%m-%d %H:%M:%S"))
        ]
        dataframe = self.spark.createDataFrame(test_data, schema)
        result = self.postgres.write_data(config, connection, dataframe)
        self.assertTrue(result)
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "actor1", "df_id": "65dc3fb832b5b2a5665841fc"}
        result = self.postgres.fetch_data(config, connection)["65dc3fb832b5b2a5665841fc"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_write_data_with_custom_config(self):
        """
        Test writing data to Postgres database table
        """
        connection = self.postgres.connect(self.connection_id["654879fe42a09b96f228302c"])
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "actor1", "df_id": "65dc3fb832b5b2a5665841fb"}
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("first_name", StringType(), True),
            StructField("last_name", StringType(), True),
            StructField("timestamp", TimestampType(), True)
        ])
        test_data = [
            (3, "Chandler", "Bing", datetime.strptime("2024-02-15 04:34:33", "%Y-%m-%d %H:%M:%S")),
            (4, "Rachel", "Green", datetime.strptime("2024-02-16 06:52:11", "%Y-%m-%d %H:%M:%S"))
        ]
        dataframe = self.spark.createDataFrame(test_data, schema)
        custom_config = {"mode": "append"}
        result = self.postgres.write_data(config, connection, dataframe, custom_config)
        self.assertTrue(result)
        config = {"connection_id": "654879fe42a09b96f228302c", "table_name": "actor1", "df_id": "65dc3fb832b5b2a5665841fc"}
        result = self.postgres.fetch_data(config, connection)["65dc3fb832b5b2a5665841fc"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_write_data_with_connection_pool(self):
        """
        Test writing data to Postgres database table
        """
        connection = self.postgres.connect(self.connection_id["654879fe42a09b96f228302d"])
        config = {"connection_id": "654879fe42a09b96f228302d", "table_name": "actor1", "df_id": "65dc3fb832b5b2a5665841fb"}
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("first_name", StringType(), True),
            StructField("last_name", StringType(), True),
            StructField("timestamp", TimestampType(), True)
        ])
        test_data = [
            (1, "Chandler", "Bing", datetime.strptime("2024-02-15 04:34:33", "%Y-%m-%d %H:%M:%S")),
            (2, "Rachel", "Green", datetime.strptime("2024-02-16 06:52:11", "%Y-%m-%d %H:%M:%S"))
        ]
        dataframe = self.spark.createDataFrame(test_data, schema)
        result = self.postgres.write_data(config, connection, dataframe)
        self.assertTrue(result)
        config = {"connection_id": "654879fe42a09b96f228302d", "table_name": "actor1", "df_id": "65dc3fb832b5b2a5665841fc"}
        result = self.postgres.fetch_data(config, connection)["65dc3fb832b5b2a5665841fc"]
        self.assertIsNotNone(result["df"])
        self.assertGreaterEqual(result["df"].count(), 1)

    def test_check_database(self):
        connection = self.postgres.connect(self.connection_id["654879fe42a09b96f228302c"])
        configuration = "public.actor"
        database, table = self.postgres.check_database(configuration, connection)
        self.assertEqual(connection["database"], database)


if __name__ == "__main__":
    unittest.main()
