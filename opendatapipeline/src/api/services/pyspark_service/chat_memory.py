from ....models.mongo.mongo_factory import MongoFactory
from ....logger.logger import Logger, logger
from ....models.connector import MongoConnector
from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase

class ChatMemory:
    
    def __init__(self,session=None):
        """
        Constructor method.

        :param session: The database session for interacting with MongoDB.
        :type session: object, optional
        """
        self.session=session
        self.mongo_connector = MongoConnector()
        self.mongo_client = self.mongo_connector.client
        self.mongo_chats = MongoFactory(self.mongo_client, "chats", session=self.session)
        self.caches: CacheBase = get_cache(session=self.session)

    def map_pandas_type_to_sql(self, pandas_type):
        mapping = {
            'int64': 'INTEGER',
            'float64': 'FLOAT',
            'object': 'VARCHAR(255)',  # Assuming string type for 'object'
            'datetime64[ns]': 'DATETIME',
            'bool': 'BOOLEAN'
        }
        return mapping.get(str(pandas_type), 'TEXT')  # Default to TEXT if not mapped

    # Function to generate SQL DDL and INSERT statements
    def generate_sql_from_dataframe(self, df, table_name):
        
        # Generate INSERT INTO SQL queries for the records in the DataFrame
        insert_queries = []
        for _, row in df.head(3).iterrows():
            values = ', '.join([f"'{value}'" if isinstance(value, str) else str(value) for value in row])
            insert_queries.append(f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({values});")
        
        # Combine CREATE TABLE and INSERT queries
        sql_script = self.pandas_to_sql_ddl(df, table_name) + "\n\n"+ f"Sample rows from {table_name} table:" + "\n" + "\n".join(insert_queries)
        
        return sql_script

    def pandas_to_sql_ddl(self, df, table_name):
        columns = []
        for column, dtype in df.dtypes.items():
            sql_type = self.map_pandas_type_to_sql(dtype)
            columns.append(f"{column} {sql_type}")
        columns_str = ",\n    ".join(columns)
        create_table_query = f"CREATE TABLE {table_name} (\n    {columns_str}\n);"
        return create_table_query
    