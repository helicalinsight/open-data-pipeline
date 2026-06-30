import uuid
from mongomock import CollectionInvalid
import os
from .shared_seed_data import *
from .create_data import setup_feather
from ..src.models.connector import MongoConnector

db = MongoConnector().client

import os
from pymongo import MongoClient, UpdateOne, errors

def setup_db():
    if os.getenv("APP_ENVIRONMENT") == "test":
        # Generate a unique database name for each test case

        collections = ['cache', 'chats', 'connections', 'conversations', 'files','schedules', 'sessions', 'users', 'langchain', 'audit_runs', 'schedule']

        # Sample data for each collection - replace these with your actual data
        data_map = {
            'chats': chats,
            'files': files,
            'users': users,
            'connections': connections,
            'cache': cache,
            'langchain': langchain,
            'audit_runs': audit_runs,
            'schedule': schedule
        }
        
        # delete collections if they already exist
        for collection_name in collections:
            try:
                db[collection_name].delete_many({})
            except Exception as e:
                pass
        
        for collection_name in collections:
            try:
                db.create_collection(collection_name)
            except errors.CollectionInvalid:
                print(f"Collection '{collection_name}' in database is invalid.")
            except errors.OperationFailure as e:
                if 'already exists' in str(e):
                    print(f"Collection '{collection_name}' in database  already exists.")
                else:
                    print(f"An error occurred in database: {e}")

            if collection_name in data_map:
                collection_data = data_map[collection_name]

                # Prepare bulk operations for upsert
                operations = [
                    UpdateOne(
                        {"_id": doc["_id"]},
                        {"$set": doc},
                        upsert=True
                    ) for doc in collection_data
                ]

                if operations:
                    try:
                        result = db[collection_name].bulk_write(operations)
                        print(f"Upserted documents in '{collection_name}' of database : Matched {result.matched_count}, Inserted {result.upserted_count}")
                    except errors.BulkWriteError as bwe:
                        print(f"Bulk write error in database: {bwe.details}")
                    except Exception as e:
                        print(f"An unexpected error occurred while upserting into '{collection_name}' in database : {e}")

        setup_feather()
    else:
        raise Exception("Set the Environment to 'test'")

    # Define the collections
    
# def setup_db():
#     if os.getenv("APP_ENVIRONMENT") not in  ["dev", "prod"]:
#         collections = ['cache', 'chats', 'connections', 'conversations', 'files', 'messages', 'schedules', 'sessions',
#                     'users', "langchain"]
#         # Create each collection
#         for collection_name in collections:
#             try:
#                 db.drop_collection(collection_name)
#                 db.create_collection(collection_name)
#                 print(f"Collection '{collection_name}' created.")
#             except CollectionInvalid:
#                 print(f"Collection '{collection_name}' already exists.")
#         db["chats"].insert_many(chats)
#         db["files"].insert_many(files)
#         db['users'].insert_many(users)
#         db["connections"].insert_many(connections)
#         db["cache"].insert_many(cache)
#         db["messages"].insert_many(messages)
#         db["langchain"].insert_many(langchain)
#     else:
#        raise Exception("Set the Envrionment to 'test'")
#     # Define the collections
 
#     setup_feather()


