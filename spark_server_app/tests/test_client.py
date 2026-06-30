from mongomock import CollectionInvalid
import os
from pymongo import MongoClient
from .shared_seed_data import *
from .create_data import *

# Allow overriding Mongo host in containerized tests
mongo_host = os.getenv("MONGO_HOST", "localhost")
client = MongoClient(f'mongodb://{mongo_host}:27017/')


def setup_db():
    # Create or access the user_sessions database
    db = client['user_sessions']
    # Define the collections
    collections = ['cache', 'schedule', 'connections', 'conversations', 'files', 'messages', 'schedules', 'sessions',
                   'users', "langchain"]

    # Create each collection
    for collection_name in collections:
        try:
            db.create_collection(collection_name)
            print(f"Collection '{collection_name}' created.")
        except CollectionInvalid:
            print(f"Collection '{collection_name}' already exists.")
    if os.getenv("APP_ENVIRONMENT") not in  ["dev", "prod"]:
        db["schedule"].insert_many(schedule)
        db["files"].insert_many(files)
        db['users'].insert_many(users)
        db["connections"].insert_many(connections)
        db["cache"].insert_many(cache)
        #db["messages"].insert_many(messages)
        db["langchain"].insert_many(langchain)
    else:
        print("Skipping data insertion in prod/development environment.")
    setup_files()

def drop_all_databases():
    if os.getenv("APP_ENVIRONMENT") not in  ["dev", "prod"]:
        databases = client.list_database_names()
        for db_name in databases:
            if db_name not in ['admin', 'config', 'local']:
                client.drop_database(db_name)
                print(f"Dropped database '{db_name}'.")
    else:
        print("Skipping dropping databases in prod/development environment.")
