from pymongo import MongoClient
import os
from src.configurations.api.config import Config
import logging


def create_root_user(host, port, username, password, database_name):
    # Connect to MongoDB

    if port:
        connection_string = f"mongodb://{username}:{password}@{host}:{port}/?authMechanism=DEFAULT&authSource={database_name}"
    else:
        connection_string = f"mongodb://{host}"
    client = MongoClient(connection_string)
    # Access admin database
    # print(client.list_database_names())
    db = client['user_sessions_test']
    # Define the collections
    collections = ['users']

    # Create each collection
    for collection_name in collections:
        try:
            db.create_collection(collection_name)
        except Exception as e: # pragma: no cover
            logging.error(f"Collection '{collection_name}' already exists: {e}", exc_info=True)


    # Create root user
    try:
        db.command("createUser", username, pwd=password, roles=[{'role': 'readWrite', 'db': 'user_sessions_test'}])
    except Exception as e: # pragma: no cover
        logging.error(e , exc_info=True)
if __name__ == "__main__":
    # MongoDB connection parameters
    MONGODB_HOST = Config.config["mongo"]["host"]
    MONGODB_PORT = Config.config["mongo"].get("port")

    # Root user credentials
    ROOT_USERNAME = Config.config["mongo"]["username"]
    ROOT_PASSWORD = os.environ.get("MONGO_PASSWORD")
    database_name = Config.config['mongo']['database']
    create_root_user(MONGODB_HOST, MONGODB_PORT, ROOT_USERNAME, ROOT_PASSWORD, database_name)


# import pymongo

# # Replace with your connection string
# connection_string = "mongodb://localhost:27017/?replicaSet=rs0"

# client = pymongo.MongoClient(connection_string)
# breakpoint()
# # Database and collection
# db = client.test_database
# collection = db.test_collection

# # Inserting a document
# result = collection.insert_one({"key": "value"})
# print(f"Inserted document id: {result.inserted_id}")

# # Querying documents
# cursor = collection.find({})
# for document in cursor:
#     print(document)

# client.close()
