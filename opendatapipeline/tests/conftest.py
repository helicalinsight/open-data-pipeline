import pymongo
import pytest
import atexit
from .test_client import setup_db


# Fixture to set up the database before running tests
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    setup_db()
    yield
    # Teardown after test is finished
    # drop_all_databases()


# import pytest
# from pymongo import MongoClient

# @pytest.fixture(scope="function", autouse=True)
# def setup_test_db():
#     """
#     Automatically creates and cleans up a test database for each test.
#     """
#     client = MongoClient("mongodb://localhost:27017")
#     test_db = client["test_db"]

#     yield test_db  # Pass the test database to the test or code being executed

#     client.drop_database("test_db")  # Clean up after the test
#     client.close()
