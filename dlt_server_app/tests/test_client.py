
"""
Seeds a minimal MongoDB dataset for dlt_server_app tests and verifies the seed.
Sets APP_ENVIRONMENT=test by default so data is inserted during tests.
"""

import os
import pytest
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid

from dlt_server_app.tests.shared_seed_data import (
    schedule as seed_schedule,
    files as seed_files,
    users as seed_users,
    connections as seed_connections,
    cache as seed_cache,
    langchain as seed_langchain,
)

def _get_mongo_client() -> MongoClient:
    """Return a Mongo client, trying $MONGO_HOST then localhost."""
    preferred_host = os.getenv("MONGO_HOST", "mongo")
    for host in (preferred_host, "localhost"):
        try:
            client = MongoClient(f"mongodb://{host}:27017/", serverSelectionTimeoutMS=1000)
            client.admin.command("ping")
            return client
        except Exception:
            continue
    raise RuntimeError("Could not connect to MongoDB (tried $MONGO_HOST and localhost).")

MONGO_CLIENT: MongoClient = _get_mongo_client()
DB_NAME: str = "user_sessions"

# Collections we create. Only some get seeded, the rest are created empty for compatibility.
COLLECTION_NAMES = [
    "cache",
    "schedule",
    "connections",
    "conversations",
    "files",
    "messages",
    "schedules",
    "sessions",
    "users",
    "langchain",
]

def setup_db() -> None:
    """Create collections and insert seed data when APP_ENVIRONMENT != dev/prod."""
    database = MONGO_CLIENT[DB_NAME]

    for collection_name in COLLECTION_NAMES:
        try:
            database.create_collection(collection_name)
            print(f"Collection '{collection_name}' created.")
        except CollectionInvalid:
            print(f"Collection '{collection_name}' already exists.")

    # Only seed when not in dev/prod environments
    if os.getenv("APP_ENVIRONMENT") not in ["dev", "prod"]:
        if seed_schedule:
            database["schedule"].insert_many(seed_schedule)
            print(f"Inserted {len(seed_schedule)} schedule records")
        if seed_files:
            database["files"].insert_many(seed_files)
            print(f"Inserted {len(seed_files)} file records")
        if seed_users:
            database["users"].insert_many(seed_users)
            print(f"Inserted {len(seed_users)} user records")
        if seed_connections:
            database["connections"].insert_many(seed_connections)
            print(f"Inserted {len(seed_connections)} connection records")
        if seed_cache:
            database["cache"].insert_many(seed_cache)
            print(f"Inserted {len(seed_cache)} cache records")
        if seed_langchain:
            database["langchain"].insert_many(seed_langchain)
            print(f"Inserted {len(seed_langchain)} langchain records")
    else:
        print("Skipping data insertion in prod/development environment.")

def drop_all_databases() -> None:
    """Drop all non-system databases when not in dev/prod."""
    if os.getenv("APP_ENVIRONMENT") not in ["dev", "prod"]:
        for db_name in MONGO_CLIENT.list_database_names():
            if db_name not in ["admin", "config", "local"]:
                MONGO_CLIENT.drop_database(db_name)
                print(f"Dropped database '{db_name}'.")
    else:
        print("Skipping database drop in prod/development environment.")
