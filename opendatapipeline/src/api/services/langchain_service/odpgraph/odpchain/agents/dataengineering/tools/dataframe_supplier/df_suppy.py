import pandas as pd
# from .....models.mongo_factory import MongoFactory
# from .....config.mongo_connector import MongoConnector
from ..........models.connector import MongoConnector
from ..........models.mongo.mongo_factory import MongoFactory
from ..........logger.logger import logger, Logger
from ..........exceptions.exception import *
from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase

mongo_connector = MongoConnector()
mongo_client=mongo_connector.client
THRESHOLD_COLUMN_NUMBER = 99999
METADATA_SAMPLE_SIZE = 5

def get_head(chat_id, session):
    """
    Retrieves the first 5 rows of the DataFrame associated with a given chat session and converts it to Markdown format.

    Args:
        chat_id (str): The ID of the chat document.
        session (object): The session object used for querying the cache.

    Returns:
        str: A Markdown representation of the first 5 rows of the DataFrame, or None if an error occurs.
    """
    try:
        cache: CacheBase = get_cache(session=session)
        chats = MongoFactory(mongo_client, "chats", session)
        succ, chat_doc=chats.get_by_id(chat_id)
        source_id = chat_doc["cwf"]["source_id"]
        cache_doc = cache.get_item(source_id, chat_doc["user_id"], chat_id)
        path=cache_doc["feather_file_path"]
        df=pd.read_feather(path)
        columns = df.columns.tolist()
        if len(columns) > THRESHOLD_COLUMN_NUMBER:
            raise Exception(f"The data appears to be too large; consider limiting the number of columns = {THRESHOLD_COLUMN_NUMBER}.")
        else:
            return str(df.head(METADATA_SAMPLE_SIZE).to_markdown())
    except ValueError as ve:
        logger.error("Value error occured: %s", ve, exc_info=True)
        return ""
    except Exception as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        raise
        
def get_datatype(chat_id):
    """
    Retrieves the data types of columns for the DataFrame associated with the given chat ID.

    Args:
        chat_id (str): The ID of the chat document.

    Returns:
        str: A string representation of the column data types, or None if an error occurs.
    """
    try:
        # TODO: There's no access to session in get_datatype so this is still using mongo directly.
        #   Looks like this is not called from anywhere, need to confirm and delete.
        cache = MongoFactory(mongo_client, "cache")
        chats = MongoFactory(mongo_client, "chats")
        succ, chat_doc=chats.get_by_id(chat_id)
        source_id=chat_doc["cwf"]["source_id"]
        _, cache_doc = cache.get_by_fields(source_id, chat_doc["user_id"], chat_id)
        metadata=cache_doc["metadata"]["column_information"]["datatypes"]
        return str(metadata)
    
    except  Exception as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        return None
        
def get_columns(chat_id, session):
    """
    Retrieves the column names of the DataFrame associated with a given chat session and converts it to Markdown format.

    Args:
        chat_id (str): The ID of the chat document.
        session (object): The session object used for querying the cache.

    Returns:
        str: A Markdown representation of the column names, or None if an error occurs.
    """
    try:
        cache: CacheBase = get_cache(session=session)
        chats = MongoFactory(mongo_client, "chats", session)
        _, chat_doc = chats.get_by_id(chat_id)
        source_id = chat_doc["cwf"]["source_id"]
        cache_doc = cache.get_item(source_id, chat_doc["user_id"], chat_id)
        path = cache_doc["feather_file_path"]
        df = pd.read_feather(path)
        columns = df.columns.tolist()
        if len(columns) > THRESHOLD_COLUMN_NUMBER:
            raise ValueError(f"The data appears to be too large; consider limiting the number of columns = {THRESHOLD_COLUMN_NUMBER}.")
        else:
            return columns
    except Exception as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        raise

def get_metadata(chat_id, session):
    """
    Generates a SQL CREATE TABLE statement based on the metadata of the DataFrame associated with a given chat session.

    Args:
        chat_id (str): The ID of the chat document.
        session (object): The session object used for querying the cache.

    Returns:
        str: A SQL CREATE TABLE statement for the DataFrame, or None if an error occurs.
    """
    try:
        cache: CacheBase = get_cache(session=session)
        chats = MongoFactory(mongo_client, "chats", session)
        succ,chat_doc=chats.get_by_id(chat_id)
        source_id=chat_doc["cwf"]["source_id"]
        cache_doc = cache.get_item(source_id, chat_doc["user_id"], chat_id)
        path=cache_doc["feather_file_path"]
        df=pd.read_feather(path)
        table_name = 'df'
        create_statement = generate_create_table_statement(df, table_name)

        return create_statement
    except  Exception as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        return None
        
def generate_create_table_statement(df, table_name):
    """
    Generates a SQL CREATE TABLE statement based on the DataFrame's schema.

    Args:
        df (pd.DataFrame): The DataFrame whose schema will be used to generate the SQL statement.
        table_name (str): The name of the table to be created.

    Returns:
        str: A SQL CREATE TABLE statement based on the DataFrame's schema.
    """
    # Mapping of pandas dtypes to SQL data types
    dtype_mapping = {
        'int64': 'INTEGER',
        'float64': 'FLOAT',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'TIMESTAMP',
        'timedelta[ns]': 'INTERVAL',
        'object': 'TEXT'
    }

    # Start the CREATE TABLE statement
    create_table_statement = f"CREATE TABLE {table_name} ("

    # Add each column name and its corresponding SQL data type
    for column in df.columns:
        dtype = str(df[column].dtype)
        sql_dtype = dtype_mapping.get(dtype, 'TEXT')  # Default to TEXT if no mapping is found
        create_table_statement += f"\n    {column} {sql_dtype},"

    # Remove the trailing comma and close the statement
    create_table_statement = create_table_statement.rstrip(',') + "\n);"

    return create_table_statement
    
    
    
    
    

    