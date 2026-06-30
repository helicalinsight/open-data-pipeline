from pymongo import MongoClient
import os

def create_root_user(host, port, username, password):
    # Connect to MongoDB
    client = MongoClient(host, port)
    # Access admin database
    # print(client.list_database_names())
    db = client['user_sessions']

    # Define the collections
    collections = ['users']

    # Create each collection
    for collection_name in collections:
        try:
            db.create_collection(collection_name)
            print(f"Collection '{collection_name}' created.")
        except Exception as e: # pragma: no cover
            print(f"Collection '{collection_name}' already exists.")


    # Create root user
    try:
        db.command("createUser", username, pwd=password, roles=[{'role': 'readWrite', 'db': 'user_sessions'}])
        print("Root user created successfully.")
    except Exception as e: # pragma: no cover
        print(e)
if __name__ == "__main__":
    # MongoDB connection parameters
    MONGODB_HOST = "127.0.0.1"
    MONGODB_PORT = 27017

    # Root user credentials
    ROOT_USERNAME = "test"
    ROOT_PASSWORD = "test"

    create_root_user(MONGODB_HOST, MONGODB_PORT, ROOT_USERNAME, ROOT_PASSWORD)
