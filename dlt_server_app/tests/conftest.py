# dlt_server_app/tests/conftest.py
import os
import pytest
import atexit
from pymongo import MongoClient
from time import sleep
from dlt_server_app.tests.test_client import setup_db, drop_all_databases

def _pick_mongo_uri():
    host = os.getenv("MONGO_HOST", "mongo")
    # try service name first, then localhost
    for h in (host, "localhost"):
        try:
            c = MongoClient(f"mongodb://{h}:27017/", serverSelectionTimeoutMS=1000)
            c.admin.command("ping")
            return f"mongodb://{h}:27017/"
        except Exception:
            continue
    raise RuntimeError("Could not reach MongoDB at either $MONGO_HOST or localhost")

@pytest.fixture(scope="session", autouse=True)
def _env_and_mongo_ready():
    # Make sure we seed in non-prod
    os.environ.setdefault("APP_ENVIRONMENT", "test")
    os.environ.setdefault("MONGO_HOST", "mongo")
    
    # Wait a moment in CI if Mongo is just starting
    uri = _pick_mongo_uri()
    client = MongoClient(uri, serverSelectionTimeoutMS=2000)
    for _ in range(10):
        try:
            client.admin.command("ping")
            break
        except Exception:
            sleep(0.5)
    yield
    # Final cleanup on session end
    drop_all_databases()

@pytest.fixture(scope="session")
def mongo_client():
    uri = _pick_mongo_uri()
    return MongoClient(uri, serverSelectionTimeoutMS=2000)

@pytest.fixture(scope="function")
def user_sessions_db(mongo_client):
    db = mongo_client["user_sessions"]
    yield db
    # Drop the test database after each test
    mongo_client.drop_database("user_sessions")

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

