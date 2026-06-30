import pytest
import atexit
from .test_client import setup_db, drop_all_databases

# Create a single shared SparkSession for the entire test session to avoid
# multiple SparkContext errors when individual tests/classes call getOrCreate()
@pytest.fixture(scope="session", autouse=True)
def _shared_spark_session():
    from pyspark.sql import SparkSession
    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName("pytest-shared-spark-session")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY")
        .getOrCreate()
    )
    yield spark
    # Only stop at the very end of the entire test session
    spark.stop()

# Fixture to set up the database before running tests
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    setup_db()
    yield
    # Teardown after test is finished
    drop_all_databases()

def delete_collections():
    # Teardown after test is finished
    drop_all_databases()

# Register delete_collections function as a teardown function
atexit.register(delete_collections)
